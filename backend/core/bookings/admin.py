from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("venue", "user", "booking_date", "start_time", "end_time", "status", "price")
    list_filter = ("status", "booking_date")
    search_fields = ("venue__name", "user__email", "user__phone")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-booking_date", "-start_time")
