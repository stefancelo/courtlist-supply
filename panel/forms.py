from django import forms
from django.utils.text import slugify

from catalogue.models import Brand, Category, Item
from core.forms import BootstrapFormMixin


class SlugFromNameMixin:
    """Lets the admin leave the slug empty: it is then made from the name,
    e.g. "Molten BG5000 game ball" -> "molten-bg5000-game-ball"."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["slug"].help_text = "Used in the page address. Leave empty to make it from the name."

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("slug") and cleaned.get("name"):
            cleaned["slug"] = slugify(cleaned["name"])
        return cleaned


class ItemForm(SlugFromNameMixin, BootstrapFormMixin, forms.ModelForm):
    """Add or edit a catalogue item, including its photo. Items go in sub-categories only."""

    class Meta:
        model = Item
        fields = [
            "name",
            "slug",
            "category",
            "brand",
            "description",
            "price",
            "colour",
            "sizes",
            "image",
            "stock",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "sizes": forms.SelectMultiple(attrs={"size": 7}),
        }
        help_texts = {
            "sizes": "Hold Ctrl to choose several, or none for one-size items.",
            "is_active": "Untick to hide the item from the shop without deleting it.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only sub-categories, shown as "Game equipment > Balls"
        self.fields["category"].queryset = Category.objects.filter(parent__isnull=False).select_related("parent")


class CategoryForm(SlugFromNameMixin, BootstrapFormMixin, forms.ModelForm):
    """Add or edit a category. No parent makes a top-level category; choosing a parent
    makes a sub-category. Only two levels are allowed."""

    class Meta:
        model = Category
        fields = ["name", "slug", "parent", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parents = Category.objects.filter(parent=None)
        if self.instance.pk:
            parents = parents.exclude(pk=self.instance.pk)
        self.fields["parent"].queryset = parents
        self.fields["parent"].empty_label = "None (top-level category)"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("parent") and self.instance.pk and self.instance.children.exists():
            self.add_error("parent", "This category has sub-categories, so it must stay top-level.")
        return cleaned


class BrandForm(SlugFromNameMixin, BootstrapFormMixin, forms.ModelForm):
    """Add or edit a brand."""

    class Meta:
        model = Brand
        fields = ["name", "slug"]




class AnalyticsFilterForm(BootstrapFormMixin, forms.Form):
    """Date range and category for the analytics dashboard."""

    start = forms.DateField(label="From", widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(label="To", widget=forms.DateInput(attrs={"type": "date"}))
    category = forms.ModelChoiceField(
        queryset=Category.objects.select_related("parent").order_by("parent__name", "name"),
        required=False,
        empty_label="All categories",
        to_field_name="slug",
    )

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start"), cleaned.get("end")
        if start and end and start > end:
            self.add_error("end", "The end date must be on or after the start date.")
        elif start and end and (end - start).days > 366:
            self.add_error("start", "Choose a period of one year at most.")
        return cleaned