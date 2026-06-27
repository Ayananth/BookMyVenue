import os
import uuid
from datetime import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from venues.availability import get_available_slots
from venues.filters import annotate_min_price, filter_venue_list
from venues.models import (
    Location,
    Venue,
    VenueCategory,
    VenueSchedule,
    VenueScheduleGroup,
    VenueScheduleGroupDay,
    VenueScheduleOverride,
    VenueStatus,
)
from venues.permissions import CanManageVenues, IsVenueOwnerOrAdmin
from venues.serializers import (
    LocationDropdownSerializer,
    VenueCategorySerializer,
    VenueDetailSerializer,
    VenueListSerializer,
    VenueScheduleGroupReadSerializer,
    VenueScheduleGroupWriteSerializer,
    VenueScheduleOverrideReadSerializer,
    VenueScheduleOverrideWriteSerializer,
    VenueUpdateSerializer,
    VenueWriteSerializer,
)


class VenuePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "limit"
    max_page_size = 50


def _base_queryset():
    return annotate_min_price(
        Venue.objects.select_related(
            "category",
            "location",
            "owner",
        ).prefetch_related("images"),
    )


def _list_queryset(request):
    queryset = _base_queryset()
    user = request.user
    mine = request.query_params.get("mine") == "true"

    if mine and user.is_authenticated and user.role == UserRole.VENUE:
        queryset = queryset.filter(owner=user)
    elif mine and user.is_authenticated and user.role == UserRole.ADMIN:
        pass
    else:
        queryset = queryset.filter(
            is_active=True,
            status=VenueStatus.APPROVED,
        )

    return filter_venue_list(queryset, request)


def _detail_queryset(request):
    queryset = _base_queryset()
    user = request.user

    if user.is_authenticated and user.role == UserRole.ADMIN:
        return queryset

    if user.is_authenticated and user.role == UserRole.VENUE:
        return queryset.filter(
            Q(is_active=True, status=VenueStatus.APPROVED)
            | Q(owner=user),
        )

    return queryset.filter(
        is_active=True,
        status=VenueStatus.APPROVED,
    )


def _detail_response(venue):
    return VenueDetailSerializer(venue).data


def _get_venue_detail(request, slug):
    return get_object_or_404(_detail_queryset(request), slug=slug)


def _create_venue(request):
    serializer = VenueWriteSerializer(
        data=request.data,
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    venue = serializer.save()
    venue = _get_venue_detail(request, venue.slug)
    return Response(
        _detail_response(venue),
        status=status.HTTP_201_CREATED,
    )


class VenueCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = VenueCategory.objects.filter(is_active=True).order_by("name")
        serializer = VenueCategorySerializer(categories, many=True)
        return Response(serializer.data)


class VenueLocationListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        locations = Location.objects.filter(is_active=True).order_by("city", "district")
        serializer = LocationDropdownSerializer(locations, many=True)
        return Response(serializer.data)


class ImageUploadView(APIView):
    permission_classes = [CanManageVenues]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"detail": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_type = getattr(file, "content_type", "") or ""
        if not content_type.startswith("image/"):
            return Response(
                {"detail": "Only image files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        extension = os.path.splitext(file.name)[1] or ".jpg"
        filename = f"venue_images/{uuid.uuid4().hex}{extension}"
        saved_path = default_storage.save(filename, file)
        image_url = request.build_absolute_uri(
            settings.MEDIA_URL + saved_path.replace("\\", "/"),
        )

        return Response(
            {
                "public_id": saved_path,
                "url": image_url,
                "secure_url": image_url,
            },
            status=status.HTTP_201_CREATED,
        )


class VenueListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageVenues()]
        return [AllowAny()]

    def get(self, request):
        queryset = _list_queryset(request)
        paginator = VenuePagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = VenueListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        return _create_venue(request)


class VenueCreateView(APIView):
    permission_classes = [CanManageVenues]

    def post(self, request):
        return _create_venue(request)


class VenueAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        venue = _get_venue_detail(request, slug)
        date_param = request.query_params.get("date")
        if not date_param:
            return Response(
                {"detail": "Query parameter 'date' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(get_available_slots(venue, target_date))


class VenueDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [CanManageVenues(), IsVenueOwnerOrAdmin()]

    def get(self, request, slug):
        venue = _get_venue_detail(request, slug)
        return Response(_detail_response(venue))

    def put(self, request, slug):
        return self._update(request, slug, partial=False)

    def patch(self, request, slug):
        return self._update(request, slug, partial=True)

    def delete(self, request, slug):
        venue = get_object_or_404(_detail_queryset(request), slug=slug)
        self.check_object_permissions(request, venue)
        venue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, slug, partial):
        venue = get_object_or_404(_detail_queryset(request), slug=slug)
        self.check_object_permissions(request, venue)

        serializer = VenueUpdateSerializer(
            venue,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        venue = serializer.save()
        venue = _get_venue_detail(request, venue.slug)
        return Response(_detail_response(venue))


def _schedule_groups_queryset(venue):
    return (
        venue.schedule_groups.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "days",
                queryset=VenueScheduleGroupDay.objects.order_by("day_of_week"),
            ),
            Prefetch(
                "schedules",
                queryset=VenueSchedule.objects.order_by("start_time"),
            ),
        )
        .order_by("created_at")
    )


def _schedule_group_response(group):
    return VenueScheduleGroupReadSerializer(group).data


def _get_schedule_group(venue, group_id):
    return get_object_or_404(
        _schedule_groups_queryset(venue),
        pk=group_id,
    )


class VenueScheduleGroupListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [CanManageVenues(), IsVenueOwnerOrAdmin()]

    def get(self, request, slug):
        venue = _get_venue_detail(request, slug)
        groups = _schedule_groups_queryset(venue)
        serializer = VenueScheduleGroupReadSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        venue = get_object_or_404(Venue.objects.select_related("owner"), slug=slug)
        self.check_object_permissions(request, venue)

        serializer = VenueScheduleGroupWriteSerializer(
            data=request.data,
            context={"venue": venue},
        )
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        group = _get_schedule_group(venue, group.pk)
        return Response(
            _schedule_group_response(group),
            status=status.HTTP_201_CREATED,
        )


class VenueScheduleGroupDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [CanManageVenues(), IsVenueOwnerOrAdmin()]

    def get(self, request, slug, group_id):
        venue = _get_venue_detail(request, slug)
        group = _get_schedule_group(venue, group_id)
        return Response(_schedule_group_response(group))

    def put(self, request, slug, group_id):
        return self._update(request, slug, group_id, partial=False)

    def patch(self, request, slug, group_id):
        return self._update(request, slug, group_id, partial=True)

    def delete(self, request, slug, group_id):
        venue = get_object_or_404(Venue.objects.select_related("owner"), slug=slug)
        self.check_object_permissions(request, venue)
        group = get_object_or_404(VenueScheduleGroup, pk=group_id, venue=venue)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, slug, group_id, partial):
        venue = get_object_or_404(Venue.objects.select_related("owner"), slug=slug)
        self.check_object_permissions(request, venue)
        group = get_object_or_404(VenueScheduleGroup, pk=group_id, venue=venue)

        serializer = VenueScheduleGroupWriteSerializer(
            group,
            data=request.data,
            partial=partial,
            context={"venue": venue, "group_id": group.pk},
        )
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        group = _get_schedule_group(venue, group.pk)
        return Response(_schedule_group_response(group))


def _schedule_overrides_queryset(venue):
    return venue.schedule_overrides.order_by("override_date", "start_time")


def _schedule_override_response(override):
    return VenueScheduleOverrideReadSerializer(override).data


def _get_schedule_override(venue, override_id):
    return get_object_or_404(
        _schedule_overrides_queryset(venue),
        pk=override_id,
    )


class VenueScheduleOverrideListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [CanManageVenues(), IsVenueOwnerOrAdmin()]

    def get(self, request, slug):
        venue = _get_venue_detail(request, slug)
        overrides = _schedule_overrides_queryset(venue)
        serializer = VenueScheduleOverrideReadSerializer(overrides, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        venue = get_object_or_404(Venue.objects.select_related("owner"), slug=slug)
        self.check_object_permissions(request, venue)

        serializer = VenueScheduleOverrideWriteSerializer(
            data=request.data,
            context={"venue": venue},
        )
        serializer.is_valid(raise_exception=True)
        override = serializer.save()
        return Response(
            _schedule_override_response(override),
            status=status.HTTP_201_CREATED,
        )


class VenueScheduleOverrideDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [CanManageVenues(), IsVenueOwnerOrAdmin()]

    def get(self, request, slug, override_id):
        venue = _get_venue_detail(request, slug)
        override = _get_schedule_override(venue, override_id)
        return Response(_schedule_override_response(override))

    def put(self, request, slug, override_id):
        return self._update(request, slug, override_id, partial=False)

    def patch(self, request, slug, override_id):
        return self._update(request, slug, override_id, partial=True)

    def delete(self, request, slug, override_id):
        venue = get_object_or_404(Venue.objects.select_related("owner"), slug=slug)
        self.check_object_permissions(request, venue)
        override = get_object_or_404(
            VenueScheduleOverride,
            pk=override_id,
            venue=venue,
        )
        override.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, slug, override_id, partial):
        venue = get_object_or_404(Venue.objects.select_related("owner"), slug=slug)
        self.check_object_permissions(request, venue)
        override = get_object_or_404(
            VenueScheduleOverride,
            pk=override_id,
            venue=venue,
        )

        serializer = VenueScheduleOverrideWriteSerializer(
            override,
            data=request.data,
            partial=partial,
            context={"venue": venue},
        )
        serializer.is_valid(raise_exception=True)
        override = serializer.save()
        return Response(_schedule_override_response(override))
