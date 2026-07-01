from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from bookings.models import Booking
from bookings.permissions import CanAccessBooking
from bookings.serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    BookingStatusUpdateSerializer,
)


class BookingPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100


def _booking_queryset(request):
    user = request.user
    queryset = Booking.objects.select_related("venue", "user").order_by(
        "-booking_date",
        "-start_time",
        "-created_at",
    )

    if user.role == UserRole.ADMIN:
        pass
    elif user.role == UserRole.VENUE:
        queryset = queryset.filter(venue__owner=user)
    else:
        queryset = queryset.filter(user=user)

    venue_slug = request.query_params.get("venue")
    if venue_slug:
        queryset = queryset.filter(venue__slug=venue_slug)

    status_param = request.query_params.get("status")
    if status_param:
        queryset = queryset.filter(status=status_param)

    return queryset


class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = _booking_queryset(request)
        paginator = BookingPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = BookingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BookingCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        bookings = serializer.save()
        response_serializer = BookingSerializer(bookings, many=True)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated, CanAccessBooking]

    def get(self, request, booking_id):
        booking = get_object_or_404(
            Booking.objects.select_related("venue", "user"),
            pk=booking_id,
        )
        self.check_object_permissions(request, booking)
        return Response(BookingSerializer(booking).data)

    def patch(self, request, booking_id):
        booking = get_object_or_404(
            Booking.objects.select_related("venue", "user"),
            pk=booking_id,
        )
        self.check_object_permissions(request, booking)

        serializer = BookingStatusUpdateSerializer(
            data=request.data,
            context={"booking": booking},
        )
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data)
