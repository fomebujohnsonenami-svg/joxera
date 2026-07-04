import django_filters

from .models import Listing, ListingMode, ListingTier


class ListingFilterSet(django_filters.FilterSet):
    """Filter published listings by field, mode, tier, and country."""

    field = django_filters.CharFilter(field_name="field", lookup_expr="iexact")
    mode = django_filters.ChoiceFilter(choices=ListingMode.choices)
    tier = django_filters.ChoiceFilter(choices=ListingTier.choices)
    country = django_filters.CharFilter(field_name="country_code", lookup_expr="iexact")

    class Meta:
        model = Listing
        fields = ["field", "mode", "tier", "country"]
