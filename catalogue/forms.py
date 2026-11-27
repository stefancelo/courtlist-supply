from django import forms
from django.db.models import Q

from core.forms import BootstrapFormMixin

from .models import Brand, Item, Rating, Size


class ItemFilterForm(BootstrapFormMixin, forms.Form):
    """The catalogue's search box and advanced filters.
    Sent with GET, so the filters appear in the page address (?q=molten&brand=nike)
    and a filtered page can be bookmarked or shared."""

    SORT_CHOICES = [
        ("name", "Name: A to Z"),
        ("price", "Price: low to high"),
        ("-price", "Price: high to low"),
        ("-created_at", "Newest first"),
    ]

    q = forms.CharField(
        label="Search",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Item or brand"}),
    )
    min_price = forms.DecimalField(label="Min price (€)", required=False, min_value=0, decimal_places=2)
    max_price = forms.DecimalField(label="Max price (€)", required=False, min_value=0, decimal_places=2)
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(), required=False, empty_label="Any brand", to_field_name="slug"
    )
    colour = forms.ChoiceField(required=False, choices=[("", "Any colour")] + Item.Colour.choices)
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(), required=False, empty_label="Any size", to_field_name="name"
    )
    sort = forms.ChoiceField(label="Sort by", required=False, choices=SORT_CHOICES)

    def clean(self):
        """Checks the price range makes sense (min not above max)."""
        cleaned = super().clean()
        low, high = cleaned.get("min_price"), cleaned.get("max_price")
        if low is not None and high is not None and low > high:
            self.add_error("max_price", "Max price must be higher than min price.")
        return cleaned

    def filter_items(self, items):
        """Returns only the items that match the search and filters, in the chosen order."""
        data = self.cleaned_data

        if data["q"]:
            items = items.filter(Q(name__icontains=data["q"]) | Q(brand__name__icontains=data["q"]))
        if data["min_price"] is not None:
            items = items.filter(price__gte=data["min_price"])
        if data["max_price"] is not None:
            items = items.filter(price__lte=data["max_price"])
        if data["brand"]:
            items = items.filter(brand=data["brand"])
        if data["colour"]:
            items = items.filter(colour=data["colour"])
        if data["size"]:
            items = items.filter(sizes=data["size"])

        return items.order_by(data["sort"] or "name")

class RatingForm(BootstrapFormMixin, forms.ModelForm):
    """Checks a submitted rating: 1 to 5 stars (the model's validators) and an optional
    review of up to 500 characters."""

    class Meta:
        model = Rating
        fields = ["stars", "review"]