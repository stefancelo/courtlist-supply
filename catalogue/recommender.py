"""Recommender: suggests items a staff member is likely to need next.

1. Interest profile: every item the user viewed (weight 1), ordered (2) or rated 4-5 stars (3),
   plus their search terms (1), adds points to that item's sub-category and brand.
2. Every other item is scored: its sub-category's points x 2, plus its brand's points.
3. Items the user already ordered and items out of stock are left out; the best scores win.
4. Users without any history get the items viewed most by all staff instead.
"""

from collections import Counter

from django.db.models import Avg, Count

from .models import Brand, Item, SearchQuery

WEIGHTS = {"view": 1, "search": 1, "order": 2, "rating": 3}
RECENT_SEARCHES = 20


def interest_profile(user):
    """Counts how interested the user is in each sub-category and brand, as two Counters
    of {id: points}."""
    categories, brands = Counter(), Counter()

    signals = [
        (Item.objects.filter(views__user=user), WEIGHTS["view"]),
        (Item.objects.filter(order_lines__order__user=user), WEIGHTS["order"]),
        (Item.objects.filter(ratings__user=user, ratings__stars__gte=4), WEIGHTS["rating"]),
    ]
    for items, weight in signals:
        for category_id, brand_id in items.values_list("category_id", "brand_id"):
            categories[category_id] += weight
            brands[brand_id] += weight

    terms = SearchQuery.objects.filter(user=user).values_list("term", flat=True)[:RECENT_SEARCHES]
    for term in terms:
        for brand_id in Brand.objects.filter(name__icontains=term).values_list("id", flat=True):
            brands[brand_id] += WEIGHTS["search"]
        for category_id in Item.objects.filter(name__icontains=term).values_list("category_id", flat=True):
            categories[category_id] += WEIGHTS["search"]

    return categories, brands


def recommend_for(user, limit=4, exclude=None):
    """Returns up to `limit` items for this user, best first. `exclude` leaves out one
    item, e.g. the one whose page is open."""
    candidates = (
        Item.objects.filter(is_active=True, stock__gt=0)
        .exclude(order_lines__order__user=user)
        .select_related("brand")
        .annotate(
            avg_rating=Avg("ratings__stars"),
            rating_count=Count("ratings", distinct=True),
            view_count=Count("views", distinct=True),
        )
    )
    if exclude is not None:
        candidates = candidates.exclude(pk=exclude.pk)

    categories, brands = interest_profile(user)
    scored = []
    for item in candidates:
        score = categories[item.category_id] * 2 + brands[item.brand_id]
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: (-pair[0], pair[1].name))
    picks = [item for _, item in scored[:limit]]

    # Too little history: fill the remaining places with the most viewed items
    if len(picks) < limit:
        chosen = {item.pk for item in picks}
        for item in candidates.order_by("-view_count", "name"):
            if item.pk not in chosen:
                picks.append(item)
            if len(picks) == limit:
                break

    return picks