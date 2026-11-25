from django.db.models import Q
from accounts.roles import staff_required
from django.shortcuts import get_object_or_404, render

from .forms import ItemFilterForm
from .models import Category, Item, SearchQuery


def record_search(request, term, items):
    """Saves a search term for the analytics dashboard and the recommender.
    Logged-in users are linked to their search; visitors are saved without a user."""
    if term:
        SearchQuery.objects.create(
            term=term.strip().lower(),
            user=request.user if request.user.is_authenticated else None,
            results_count=items.count(),
        )

@staff_required
def item_list(request, slug=None):
    """Catalogue page. Shows all active items or one category's items,
    narrowed down by the search box and the advanced filters.
    A top-level category also includes the items of all its sub-categories."""
    items = Item.objects.filter(is_active=True).select_related("brand", "category")
    category = None

    if slug:
        category = get_object_or_404(Category, slug=slug)
        # Items in this category itself OR in one of its sub-categories
        items = items.filter(Q(category=category) | Q(category__parent=category))

    # The form reads the filters from the address; with no filters it stays empty (unbound)
    filter_form = ItemFilterForm(request.GET or None)
    if filter_form.is_valid():
        items = filter_form.filter_items(items)
        record_search(request, filter_form.cleaned_data["q"], items)

    # Top-level categories for the sidebar; their sub-categories are fetched in the same go
    categories = Category.objects.filter(parent=None).prefetch_related("children")

    context = {
        "items": items,
        "category": category,
        "categories": categories,
        "filter_form": filter_form,
        "page_title": category.name if category else "Catalogue",
    }
    return render(request, "catalogue/item_list.html", context)

@staff_required
def item_detail(request, slug):
    """One item's page: image, price, brand, colour, sizes and stock."""
    item = get_object_or_404(
        Item.objects.select_related("brand", "category__parent"),
        slug=slug,
        is_active=True,
    )
    return render(request, "catalogue/item_detail.html", {"item": item})