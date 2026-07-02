from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.exceptions import (
    BookingError,
    InvalidBookingDateError,
    RazorpayOrderCreationError,
    ScheduleUnavailableError,
    SlotAlreadyBookedError,
    SlotLockedError,
    VenueNotAvailableError,
    VenueScheduleNotFoundError,
)
from bookings.models import Booking
from bookings.permissions import CanAccessBooking
from bookings.serializers import (
    BookingDetailSerializer,
    BookingListSerializer,
    BookingStartResponseSerializer,
    BookingStartSerializer,
    BookingStatusUpdateSerializer,
)
from bookings.services.booking_service import BookingService

BOOKING_ERROR_STATUS = {
    VenueScheduleNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidBookingDateError: status.HTTP_400_BAD_REQUEST,
    VenueNotAvailableError: status.HTTP_400_BAD_REQUEST,
    ScheduleUnavailableError: status.HTTP_400_BAD_REQUEST,
    SlotAlreadyBookedError: status.HTTP_409_CONFLICT,
    SlotLockedError: status.HTTP_409_CONFLICT,
    RazorpayOrderCreationError: status.HTTP_502_BAD_GATEWAY,
}


class BookingPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100


BOOKING_DETAIL_SELECT_RELATED = (
    "payment",
    "venue_schedule",
    "venue_schedule__group",
    "venue_schedule__group__venue",
    "venue_schedule__group__venue__category",
    "venue_schedule__group__venue__city",
    "venue_schedule__group__venue__city__district",
)


class BookingStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = BookingService.start_booking(
                user=request.user,
                venue_schedule_id=serializer.validated_data["venue_schedule_id"],
                booking_date=serializer.validated_data["booking_date"],
            )
        except BookingError as exc:
            return Response(
                {"message": exc.message},
                status=BOOKING_ERROR_STATUS.get(
                    type(exc),
                    status.HTTP_400_BAD_REQUEST,
                ),
            )

        response_serializer = BookingStartResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class BookingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = BookingService.get_user_bookings(request.user)
        paginator = BookingPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = BookingListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated, CanAccessBooking]

    def get(self, request, booking_id):
        booking = get_object_or_404(
            Booking.objects.select_related(*BOOKING_DETAIL_SELECT_RELATED),
            pk=booking_id,
        )
        self.check_object_permissions(request, booking)
        return Response(BookingDetailSerializer(booking).data)

    def patch(self, request, booking_id):
        booking = get_object_or_404(
            Booking.objects.select_related(*BOOKING_DETAIL_SELECT_RELATED),
            pk=booking_id,
        )
        self.check_object_permissions(request, booking)

        serializer = BookingStatusUpdateSerializer(
            data=request.data,
            context={"booking": booking},
        )
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingDetailSerializer(booking).data)
