from decimal import Decimal, InvalidOperation

from django.db.models import Case, Exists, IntegerField, Min, OuterRef, Q, Value, When
from rest_framework.filters import OrderingFilter

from venues.models import City, VenueSchedule


class VenueFilterBackend:
    def filter_queryset(self, request, queryset):
        search = request.query_params.get("search")
        if search is not None:
            search = search.strip()
            if search:
                queryset = queryset.filter(name__icontains=search)

        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        min_price = _parse_decimal(request.query_params.get("min_price"))
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)

        max_price = _parse_decimal(request.query_params.get("max_price"))
        if max_price is not None:
            queryset = queryset.filter(min_price__lte=max_price)

        return queryset


class VenueOrderingFilter(OrderingFilter):
    ordering_fields = ["min_price", "created_at", "name", "capacity"]
    ordering = ["-created_at"]


def annotate_min_price(queryset):
    return queryset.annotate(
        min_price=Min(
            "schedule_groups__schedules__price",
            filter=Q(
                schedule_groups__is_active=True,
                schedule_groups__schedules__is_available=True,
            ),
        ),
    )


def annotate_has_slots(queryset):
    return queryset.annotate(
        has_slots=Exists(
            VenueSchedule.objects.filter(
                group__venue=OuterRef("pk"),
                group__is_active=True,
            ),
        ),
    )


def apply_city_district_priority(queryset, city_id):
    try:
        city_pk = int(city_id)
    except (TypeError, ValueError):
        return queryset, False

    district_id = (
        City.objects.filter(pk=city_pk)
        .values_list("district_id", flat=True)
        .first()
    )
    if district_id is None:
        return queryset.none(), False

    queryset = queryset.filter(city__district_id=district_id)
    queryset = queryset.annotate(
        location_priority=Case(
            When(city_id=city_pk, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
    )
    return queryset, True


def filter_venue_list(queryset, request):
    queryset = VenueFilterBackend().filter_queryset(request, queryset)

    city_id = request.query_params.get("city_id")
    uses_location_priority = False
    if city_id:
        queryset, uses_location_priority = apply_city_district_priority(
            queryset,
            city_id,
        )

    ordering_filter = VenueOrderingFilter()
    secondary_ordering = ordering_filter.get_ordering(
        request,
        queryset,
        _ListFilterView(),
    )
    if not secondary_ordering:
        secondary_ordering = VenueOrderingFilter.ordering

    if uses_location_priority:
        return queryset.order_by("location_priority", *secondary_ordering)

    return ordering_filter.filter_queryset(
        request,
        queryset,
        _ListFilterView(),
    )


class _ListFilterView:
    ordering_fields = VenueOrderingFilter.ordering_fields
    ordering = VenueOrderingFilter.ordering


def _parse_decimal(value: str | None) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None
