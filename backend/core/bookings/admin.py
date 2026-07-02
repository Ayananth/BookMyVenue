from django.contrib import admin

from bookings.models import Booking, BookingSession, Payment


@admin.register(BookingSession)
class BookingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "venue_schedule",
        "booking_date",
        "locked_price",
        "status",
        "expires_at",
    )
    list_filter = ("status", "booking_date")
    search_fields = ("user__email", "user__phone", "venue_schedule__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking_session", "razorpay_order_id", "amount", "status")
    list_filter = ("status", "provider")
    search_fields = ("razorpay_order_id", "razorpay_payment_id")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "venue_schedule",
        "booking_date",
        "booking_amount",
        "status",
        "confirmed_at",
    )
    list_filter = ("status", "booking_date")
    search_fields = ("user__email", "user__phone", "venue_schedule__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-booking_date", "-created_at")
    autocomplete_fields = ("user", "venue_schedule")
