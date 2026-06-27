from django.conf import settings
from django.db import models
from django.db.models import F, Q


class BookingType(models.TextChoices):
    HOURLY = "hourly", "Hourly"
    SESSION = "session", "Session"
    FULL_DAY = "full_day", "Full Day"


class VenueStatus(models.TextChoices):
    APPROVED = "approved", "Approved"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    REJECTED = "rejected", "Rejected"
    SUSPENDED = "suspended", "Suspended"


class Location(models.Model):
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "locations"
        constraints = [
            models.CheckConstraint(
                condition=Q(latitude__isnull=True)
                | (Q(latitude__gte=-90) & Q(latitude__lte=90)),
                name="ck_locations_latitude",
            ),
            models.CheckConstraint(
                condition=Q(longitude__isnull=True)
                | (Q(longitude__gte=-180) & Q(longitude__lte=180)),
                name="ck_locations_longitude",
            ),
        ]
        indexes = [
            models.Index(fields=["city"], name="ix_locations_city"),
        ]

    def __str__(self) -> str:
        return f"{self.city}, {self.district}"


class VenueCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_url = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "venue_categories"
        verbose_name_plural = "venue categories"

    def __str__(self) -> str:
        return self.name


class Venue(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="venues",
    )
    category = models.ForeignKey(
        VenueCategory,
        on_delete=models.PROTECT,
        related_name="venues",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="venues",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    address = models.TextField()
    capacity = models.PositiveIntegerField()
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=VenueStatus.choices,
        default=VenueStatus.PENDING_APPROVAL,
    )
    amenities = models.JSONField(default=list)
    booking_type = models.CharField(max_length=20, choices=BookingType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "venues"
        constraints = [
            models.CheckConstraint(
                condition=Q(capacity__gt=0),
                name="ck_venues_capacity_positive",
            ),
        ]
        indexes = [
            models.Index(fields=["owner"], name="ix_venues_owner_id"),
            models.Index(fields=["category"], name="ix_venues_category_id"),
            models.Index(fields=["location"], name="ix_venues_location_id"),
            models.Index(fields=["status"], name="ix_venues_status"),
            models.Index(
                fields=["category", "status"],
                name="ix_venues_category_status",
            ),
            models.Index(
                fields=["location", "status"],
                name="ix_venues_location_status",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class VenueImage(models.Model):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image_url = models.TextField()
    is_cover = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "venue_images"
        indexes = [
            models.Index(fields=["venue"], name="ix_venue_images_venue_id"),
            models.Index(
                fields=["venue", "sort_order"],
                name="ix_venue_images_venue_sort",
            ),
        ]

    def __str__(self) -> str:
        return f"Image #{self.pk}"


class VenueScheduleGroup(models.Model):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name="schedule_groups",
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "venue_schedule_groups"

    def __str__(self) -> str:
        return self.name


class VenueScheduleGroupDay(models.Model):
    group = models.ForeignKey(
        VenueScheduleGroup,
        on_delete=models.CASCADE,
        related_name="days",
    )
    day_of_week = models.IntegerField()

    class Meta:
        db_table = "venue_schedule_group_days"
        constraints = [
            models.UniqueConstraint(
                fields=["group", "day_of_week"],
                name="uq_group_day",
            ),
            models.CheckConstraint(
                condition=Q(day_of_week__gte=0) & Q(day_of_week__lte=6),
                name="ck_day_of_week",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.group.name} - day {self.day_of_week}"


class VenueSchedule(models.Model):
    group = models.ForeignKey(
        VenueScheduleGroup,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "venue_schedules"
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="ck_schedule_time_range",
            ),
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="ck_schedule_price",
            ),
            models.UniqueConstraint(
                fields=["group", "start_time", "end_time"],
                name="uq_schedule_slot",
            ),
        ]

    def __str__(self) -> str:
        label = self.name or "Schedule"
        return f"{label} ({self.start_time}-{self.end_time})"


class VenueScheduleOverride(models.Model):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name="schedule_overrides",
    )
    override_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    is_available = models.BooleanField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "venue_schedule_overrides"
        indexes = [
            models.Index(fields=["venue"], name="ix_sched_override_venue"),
            models.Index(fields=["override_date"], name="ix_sched_override_date"),
        ]

    def __str__(self) -> str:
        return f"{self.venue.name} - {self.override_date}"
