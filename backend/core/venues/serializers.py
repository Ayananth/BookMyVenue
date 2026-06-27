from rest_framework import serializers

from accounts.models import UserRole
from venues.models import (
    BookingType,
    Location,
    Venue,
    VenueCategory,
    VenueImage,
    VenueStatus,
)
from venues.utils import generate_unique_venue_slug


class LocationDropdownSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ("id", "name")

    def get_name(self, obj) -> str:
        return f"{obj.city}, {obj.district}"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("id", "city", "district", "state")


class VenueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueCategory
        fields = ("id", "name", "icon_url")


class VenueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImage
        fields = ("id", "image_url", "is_cover", "sort_order", "uploaded_at")
        read_only_fields = fields


class VenueImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImage
        fields = ("image_url", "is_cover", "sort_order")


class VenueListSerializer(serializers.ModelSerializer):
    category = VenueCategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = (
            "slug",
            "name",
            "address",
            "capacity",
            "status",
            "is_active",
            "booking_type",
            "category",
            "location",
            "min_price",
            "cover_image",
            "created_at",
        )

    def get_cover_image(self, obj) -> str | None:
        images = list(obj.images.all())
        if not images:
            return None
        cover = next((image for image in images if image.is_cover), None)
        image = cover or min(images, key=lambda item: item.sort_order)
        return image.image_url


class VenueDetailSerializer(serializers.ModelSerializer):
    category = VenueCategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    images = VenueImageSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Venue
        fields = (
            "slug",
            "owner_id",
            "name",
            "description",
            "address",
            "capacity",
            "contact_name",
            "contact_phone",
            "contact_email",
            "status",
            "amenities",
            "booking_type",
            "is_active",
            "category",
            "location",
            "images",
            "min_price",
            "created_at",
            "updated_at",
        )


def save_venue_images(venue, images_data):
    if not images_data:
        return

    VenueImage.objects.bulk_create(
        [
            VenueImage(
                venue=venue,
                image_url=image["image_url"],
                is_cover=image.get("is_cover", False),
                sort_order=image.get("sort_order", index),
            )
            for index, image in enumerate(images_data)
        ],
    )


class VenueWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=VenueCategory.objects.filter(is_active=True),
    )
    location_id = serializers.PrimaryKeyRelatedField(
        source="location",
        queryset=Location.objects.filter(is_active=True),
    )
    images = VenueImageCreateSerializer(many=True, required=False, default=list)

    class Meta:
        model = Venue
        fields = (
            "category_id",
            "location_id",
            "name",
            "description",
            "address",
            "capacity",
            "booking_type",
            "contact_name",
            "contact_phone",
            "contact_email",
            "amenities",
            "images",
        )

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0.")
        return value

    def validate_booking_type(self, value):
        if value not in BookingType.values:
            raise serializers.ValidationError("Invalid booking type.")
        return value

    def validate_images(self, value):
        if not value:
            return value

        cover_count = sum(1 for image in value if image.get("is_cover"))
        if cover_count > 1:
            raise serializers.ValidationError("Only one cover image is allowed.")
        if cover_count == 0:
            value[0]["is_cover"] = True
        return value

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        owner = self.context["request"].user
        name = validated_data["name"]
        validated_data["slug"] = generate_unique_venue_slug(name)
        venue = Venue.objects.create(owner=owner, **validated_data)
        save_venue_images(venue, images_data)
        return venue

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images_data is not None:
            instance.images.all().delete()
            save_venue_images(instance, images_data)

        return instance


class VenueUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=VenueCategory.objects.filter(is_active=True),
        required=False,
    )
    location_id = serializers.PrimaryKeyRelatedField(
        source="location",
        queryset=Location.objects.filter(is_active=True),
        required=False,
    )
    images = VenueImageCreateSerializer(many=True, required=False)
    slug = serializers.SlugField(required=False, max_length=220)

    class Meta:
        model = Venue
        fields = (
            "slug",
            "category_id",
            "location_id",
            "name",
            "description",
            "address",
            "capacity",
            "booking_type",
            "contact_name",
            "contact_phone",
            "contact_email",
            "amenities",
            "status",
            "is_active",
            "images",
        )
        extra_kwargs = {
            "name": {"required": False},
            "address": {"required": False},
            "capacity": {"required": False},
            "booking_type": {"required": False},
            "contact_name": {"required": False},
            "contact_phone": {"required": False},
            "contact_email": {"required": False},
        }

    def validate_slug(self, value):
        queryset = Venue.objects.filter(slug=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("This slug is already in use.")
        return value

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0.")
        return value

    def validate_status(self, value):
        user = self.context["request"].user
        if user.role != UserRole.ADMIN and value != self.instance.status:
            raise serializers.ValidationError(
                "Only admins can change venue status.",
            )
        if value not in VenueStatus.values:
            raise serializers.ValidationError("Invalid status.")
        return value

    def validate_images(self, value):
        if value is None:
            return value
        cover_count = sum(1 for image in value if image.get("is_cover"))
        if cover_count > 1:
            raise serializers.ValidationError("Only one cover image is allowed.")
        if value and cover_count == 0:
            value[0]["is_cover"] = True
        return value

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images_data is not None:
            instance.images.all().delete()
            save_venue_images(instance, images_data)

        return instance
