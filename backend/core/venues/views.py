from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from venues.filters import annotate_min_price, filter_venue_list
from venues.models import Venue, VenueStatus
from venues.permissions import CanManageVenues, IsVenueOwnerOrAdmin
from venues.serializers import (
    VenueDetailSerializer,
    VenueListSerializer,
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
