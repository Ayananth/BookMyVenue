from decimal import Decimal, InvalidOperation

from django.db.models import Min, Q
from rest_framework.filters import OrderingFilter


class VenueFilterBackend:
    def filter_queryset(self, request, queryset):
        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        city_id = request.query_params.get("city_id")
        if city_id:
            queryset = queryset.filter(city_id=city_id)

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


def filter_venue_list(queryset, request):
    queryset = VenueFilterBackend().filter_queryset(request, queryset)
    return VenueOrderingFilter().filter_queryset(
        request,
        queryset,
        view=_ListFilterView(),
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
