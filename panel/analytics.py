"""Analytics for the admin panel. Every statistic is calculated by the database with
annotate(), Count, Sum and Avg, never by looping over rows in Python."""

from datetime import timedelta

from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncDate

from catalogue.models import Item, ItemView, SearchQuery
from orders.models import OrderItem

TOP = 5

# Price x quantity of one order line, worked out inside the database
LINE_REVENUE = ExpressionWrapper(F("unit_price") * F("quantity"), output_field=DecimalField(max_digits=12, decimal_places=2))


def in_category(prefix, category):
    """A filter for "belongs to this category or one of its sub-categories".
    prefix is the path from the model to the item, e.g. "item__" for an order line."""
    if category is None:
        return Q()
    return Q(**{f"{prefix}category": category}) | Q(**{f"{prefix}category__parent": category})


def build_analytics(start, end, category=None):
    """All dashboard statistics for the dates start..end (both included), optionally
    for one category. Returns plain values that can go straight into JSON."""
    lines = OrderItem.objects.filter(
        order__created_at__date__gte=start,
        order__created_at__date__lte=end,
    ).filter(in_category("item__", category))

    totals = lines.aggregate(orders=Count("order", distinct=True), revenue=Sum(LINE_REVENUE))

    per_day = {
        row["day"]: row
        for row in lines.annotate(day=TruncDate("order__created_at"))
        .values("day")
        .annotate(orders=Count("order", distinct=True), revenue=Sum(LINE_REVENUE))
    }
    days = [start + timedelta(days=offset) for offset in range((end - start).days + 1)]

    best_sellers = (
        lines.values("item__name").annotate(sold=Sum("quantity")).order_by("-sold", "item__name")[:TOP]
    )

    ratings_in_period = Q(ratings__updated_at__date__gte=start, ratings__updated_at__date__lte=end)
    top_rated = (
        Item.objects.filter(in_category("", category))
        .annotate(
            average=Avg("ratings__stars", filter=ratings_in_period),
            count=Count("ratings", filter=ratings_in_period),
        )
        .filter(count__gt=0)
        .order_by("-average", "-count", "name")[:TOP]
    )

    viewed = (
        ItemView.objects.filter(viewed_at__date__gte=start, viewed_at__date__lte=end)
        .filter(in_category("item__", category))
        .values("item__category__name")
        .annotate(views=Count("id"))
        .order_by("-views", "item__category__name")[:TOP]
    )

    searched = (
        SearchQuery.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("term")
        .annotate(times=Count("id"))
        .order_by("-times", "term")[:TOP]
    )

    return {
        "totals": {"orders": totals["orders"], "revenue": f"{totals['revenue'] or 0:.2f}"},
        "sales": {
            "labels": [day.strftime("%d %b") for day in days],
            "orders": [per_day[day]["orders"] if day in per_day else 0 for day in days],
            "revenue": [round(float(per_day[day]["revenue"]), 2) if day in per_day else 0 for day in days],
        },
        "best_sellers": {
            "labels": [row["item__name"] for row in best_sellers],
            "values": [row["sold"] for row in best_sellers],
        },
        "top_rated": {
            "labels": [item.name for item in top_rated],
            "values": [round(item.average, 2) for item in top_rated],
        },
        "most_viewed": {
            "labels": [row["item__category__name"] for row in viewed],
            "values": [row["views"] for row in viewed],
        },
        "searches": {
            "labels": [row["term"] for row in searched],
            "values": [row["times"] for row in searched],
        },
    }