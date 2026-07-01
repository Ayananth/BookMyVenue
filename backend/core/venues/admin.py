from django.contrib import admin

from .models import (
    City,
    District,
    Venue,
    VenueCategory,
    VenueImage,
    VenueSchedule,
    VenueScheduleGroup,
    VenueScheduleGroupDay,
    VenueScheduleOverride,
)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "district")
    list_filter = ("district",)
    search_fields = ("name", "district__name")
    ordering = ("district__name", "name")


@admin.register(VenueCategory)
class VenueCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 0
    fields = ("image_url", "is_cover", "sort_order", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "category",
        "city",
        "status",
        "booking_type",
        "is_active",
        "created_at",
    )
    list_filter = ("status", "booking_type", "is_active", "category", "city__district")
    search_fields = ("name", "slug", "owner__email", "owner__phone", "contact_email")
    readonly_fields = ("slug", "created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = (VenueImageInline,)
    autocomplete_fields = ("owner", "category", "city")


@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ("venue", "is_cover", "sort_order", "uploaded_at")
    list_filter = ("is_cover",)
    search_fields = ("venue__name",)
    readonly_fields = ("uploaded_at",)
    ordering = ("venue__name", "sort_order")
    autocomplete_fields = ("venue",)


class VenueScheduleGroupDayInline(admin.TabularInline):
    model = VenueScheduleGroupDay
    extra = 0
    fields = ("day_of_week",)


class VenueScheduleInline(admin.TabularInline):
    model = VenueSchedule
    extra = 0
    fields = ("name", "start_time", "end_time", "price", "is_available")
    readonly_fields = ("created_at", "updated_at")


@admin.register(VenueScheduleGroup)
class VenueScheduleGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "venue", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "venue__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("venue__name", "name")
    inlines = (VenueScheduleGroupDayInline, VenueScheduleInline)
    autocomplete_fields = ("venue",)


@admin.register(VenueScheduleGroupDay)
class VenueScheduleGroupDayAdmin(admin.ModelAdmin):
    list_display = ("group", "day_of_week")
    list_filter = ("day_of_week",)
    search_fields = ("group__name", "group__venue__name")
    ordering = ("group__venue__name", "day_of_week")
    autocomplete_fields = ("group",)


@admin.register(VenueSchedule)
class VenueScheduleAdmin(admin.ModelAdmin):
    list_display = ("group", "name", "start_time", "end_time", "price", "is_available")
    list_filter = ("is_available",)
    search_fields = ("name", "group__name", "group__venue__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("group__venue__name", "start_time")
    autocomplete_fields = ("group",)


@admin.register(VenueScheduleOverride)
class VenueScheduleOverrideAdmin(admin.ModelAdmin):
    list_display = (
        "venue",
        "override_date",
        "start_time",
        "end_time",
        "is_available",
        "created_at",
    )
    list_filter = ("is_available", "override_date")
    search_fields = ("venue__name", "reason")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-override_date",)
    autocomplete_fields = ("venue",)
