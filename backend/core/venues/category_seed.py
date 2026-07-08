from venues.data.venue_categories import VENUE_CATEGORIES


def seed_venue_categories(*, VenueCategory):
    """Create default venue categories for local development."""
    created = 0

    for name in VENUE_CATEGORIES:
        _, was_created = VenueCategory.objects.get_or_create(
            name=name,
            defaults={"is_active": True},
        )
        if was_created:
            created += 1

    return {"created": created}
