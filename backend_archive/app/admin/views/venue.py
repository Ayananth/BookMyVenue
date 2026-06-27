from sqladmin import ModelView

from app.models.venue import (
    Location,
    VenueCategory,
    Venue,
    VenueImage,
    VenueSlot,
)


class LocationAdmin(ModelView, model=Location):
    name = "Location"
    name_plural = "Locations"

    can_export = True
    page_size = 25

    column_list = [
        Location.id,
        Location.city,
        Location.district,
        Location.state,
        Location.is_active,
        Location.created_at,
    ]

    column_searchable_list = [
        "city",
        "district",
        "state",
    ]

    column_sortable_list = [
        Location.id,
        Location.city,
        Location.created_at,
    ]

    # Uncomment if filters work in your setup
    # column_filters = [
    #     "city",
    #     "state",
    #     "is_active",
    # ]


class VenueCategoryAdmin(ModelView, model=VenueCategory):
    name = "Venue Category"
    name_plural = "Venue Categories"

    can_export = True
    page_size = 25

    column_list = [
        VenueCategory.id,
        VenueCategory.name,
        VenueCategory.is_active,
    ]

    column_searchable_list = [
        "name",
    ]

    column_sortable_list = [
        VenueCategory.id,
        VenueCategory.name,
    ]

    # column_filters = [
    #     "is_active",
    # ]


class VenueAdmin(ModelView, model=Venue):
    name = "Venue"
    name_plural = "Venues"

    can_export = True
    page_size = 25

    column_default_sort = [
        (Venue.created_at, True)
    ]

    column_list = [
        Venue.id,
        Venue.name,
        Venue.owner,
        Venue.category,
        Venue.location,
        Venue.capacity,
        Venue.status,
        Venue.is_active,
        Venue.created_at,
    ]

    column_searchable_list = [
        "name",
        "address",
    ]

    column_sortable_list = [
        Venue.id,
        Venue.name,
        Venue.capacity,
        Venue.created_at,
    ]

    # column_filters = [
    #     "status",
    #     "is_active",
    # ]

    form_columns = [
        Venue.owner,
        Venue.category,
        Venue.location,
        Venue.name,
        Venue.description,
        Venue.address,
        Venue.capacity,
        Venue.status,
        Venue.amenities,
        Venue.is_active,
    ]


class VenueImageAdmin(ModelView, model=VenueImage):
    name = "Venue Image"
    name_plural = "Venue Images"

    can_export = True
    page_size = 25

    column_list = [
        VenueImage.id,
        VenueImage.venue,
        VenueImage.is_cover,
        VenueImage.sort_order,
        VenueImage.uploaded_at,
    ]

    column_sortable_list = [
        VenueImage.id,
        VenueImage.sort_order,
        VenueImage.uploaded_at,
    ]

    form_columns = [
        VenueImage.venue,
        VenueImage.image_url,
        VenueImage.is_cover,
        VenueImage.sort_order,
    ]

    # column_filters = [
    #     "is_cover",
    # ]


class VenueSlotAdmin(ModelView, model=VenueSlot):
    name = "Venue Slot"
    name_plural = "Venue Slots"

    can_export = True
    page_size = 25

    column_default_sort = [
        (VenueSlot.slot_date, True)
    ]

    column_list = [
        VenueSlot.id,
        VenueSlot.venue,
        VenueSlot.slot_date,
        VenueSlot.start_time,
        VenueSlot.end_time,
        VenueSlot.price,
        VenueSlot.is_available,
    ]

    column_sortable_list = [
        VenueSlot.slot_date,
        VenueSlot.start_time,
        VenueSlot.price,
    ]

    form_columns = [
        VenueSlot.venue,
        VenueSlot.slot_date,
        VenueSlot.start_time,
        VenueSlot.end_time,
        VenueSlot.price,
        VenueSlot.is_available,
    ]

    # column_filters = [
    #     "slot_date",
    #     "is_available",
    # ]