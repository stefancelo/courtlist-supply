from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Item


def item_list(request, slug=None):
    """Catalogue page. Shows all active items, or only those in one category.
    A top-level category also includes the items of all its sub-categories."""
    items = Item.objects.filter(is_active=True).select_related("brand", "category")
    category = None

    if slug:
        category = get_object_or_404(Category, slug=slug)
        # Items in this category itself OR in one of its sub-categories
        items = items.filter(Q(category=category) | Q(category__parent=category))

    # Top-level categories for the sidebar; their sub-categories are fetched in the same go
    categories = Category.objects.filter(parent=None).prefetch_related("children")

    context = {
        "items": items,
        "category": category,
        "categories": categories,
        "page_title": category.name if category else "Catalogue",
    }
    return render(request, "catalogue/item_list.html", context)


def item_detail(request, slug):
    """One item's page: image, price, brand, colour, sizes and stock."""
    item = get_object_or_404(
        Item.objects.select_related("brand", "category__parent"),
        slug=slug,
        is_active=True,
    )
    return render(request, "catalogue/item_detail.html", {"item": item})