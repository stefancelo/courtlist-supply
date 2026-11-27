from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from accounts.roles import staff_required
from orders.models import OrderItem

from .forms import ItemFilterForm, RatingForm
from .models import Category, Item, ItemView, Rating, SearchQuery
from .recommender import recommend_for


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
    items = (
        Item.objects.filter(is_active=True)
        .select_related("brand", "category")
        .annotate(avg_rating=Avg("ratings__stars"), rating_count=Count("ratings", distinct=True))
    )
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

def has_ordered(user, item):
    """True if the user has ordered this item at least once. Only buyers may rate an item."""
    return OrderItem.objects.filter(order__user=user, item=item).exists()

def rating_summary(item):
    """An item's average stars and number of ratings, calculated by the database."""
    return item.ratings.aggregate(average=Avg("stars"), count=Count("id"))


def latest_reviews(item):
    """The five most recent ratings of an item that include a written review."""
    return item.ratings.select_related("user").exclude(review="")[:5]


@staff_required
def item_detail(request, slug):
    """One item's page: details, the add-to-cart form, its ratings and reviews.
    Each visit is recorded for "recently viewed", the recommender and the analytics."""
    item = get_object_or_404(
        Item.objects.select_related("brand", "category__parent"),
        slug=slug,
        is_active=True,
    )
    ItemView.objects.create(item=item, user=request.user)

    context = {
        "item": item,
        "can_rate": has_ordered(request.user, item),
        "own_rating": item.ratings.filter(user=request.user).first(),
        "reviews": latest_reviews(item),
        "recommendations": recommend_for(request.user, exclude=item),
        **rating_summary(item),
    }
    return render(request, "catalogue/item_detail.html", context)


@staff_required
@require_POST
def rate_item(request, item_id):
    """Saves the logged-in user's rating of an item: a new one, or an update of theirs.
    Called by fetch from rating.js, it answers with JSON, including the refreshed summary
    and reviews as HTML; as a normal form (JavaScript off) it redirects back to the item."""
    item = get_object_or_404(Item, pk=item_id, is_active=True)
    form = RatingForm(request.POST)
    is_fetch = request.headers.get("X-Requested-With") == "fetch"

    # Only staff who have ordered the item may rate it, checked here as well as in the page
    if not has_ordered(request.user, item):
        error = "You can only rate items you have ordered."
        if is_fetch:
            return JsonResponse({"ok": False, "message": error}, status=403)
        messages.error(request, error)
        return redirect(item)

    if not form.is_valid():
        error = "Choose between 1 and 5 stars, and keep the review under 500 characters."
        if is_fetch:
            return JsonResponse({"ok": False, "message": error}, status=400)
        messages.error(request, error)
        return redirect(item)

    Rating.objects.update_or_create(item=item, user=request.user, defaults=form.cleaned_data)
    success = "Thanks, your rating is saved."

    if is_fetch:
        context = {**rating_summary(item), "reviews": latest_reviews(item)}
        return JsonResponse(
            {
                "ok": True,
                "message": success,
                "summary_html": render_to_string("catalogue/partials/rating_summary.html", context),
                "reviews_html": render_to_string("catalogue/partials/review_list.html", context),
            }
        )
    messages.success(request, success)
    return redirect(item)