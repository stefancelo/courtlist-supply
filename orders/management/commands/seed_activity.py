"""seed_activity: fills the last 30 days with demo activity, so the analytics dashboard,
the personal dashboard and the recommender have something to show: orders, ratings,
item views and searches.

Usage:  python manage.py seed_activity      (after seed_teams, seed_demo and seed_users)

It uses demo_staff plus three extra staff accounts that can't log in (they only make
the data more varied). Running it again first removes the activity it made last time,
so the numbers never pile up. A fixed random seed gives the same data on every machine.
"""

import random
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from accounts.roles import STAFF_GROUP
from catalogue.models import Item, ItemView, Rating, SearchQuery
from gameweek.models import Team
from orders.models import Order, OrderItem

DAYS = 30

# (username, first name, last name, club slug) of the extra staff accounts
EXTRA_STAFF = [
    ("staff_olympiacos", "Giorgos", "Petrou", "olympiacos"),
    ("staff_real_madrid", "Lucia", "Navarro", "real-madrid"),
    ("staff_zalgiris", "Tomas", "Kazlauskas", "zalgiris"),
]

SEARCH_TERMS = [
    "molten", "ball", "nike", "polo", "tape", "whistle",
    "fox 40", "towel", "first aid", "jacket", "hyperice", "shot clock",
]

REVIEWS = {
    5: "Exactly what we needed on game night.",
    4: "Good quality, arrived quickly.",
    3: "Does the job.",
    2: "Wore out faster than expected.",
}


def save_with_dates(model, rows, date_fields):
    """Saves (object, datetime) pairs in bulk, then gives each row its own date.
    Needed because auto_now_add and auto_now fields always use "now" when a row is created."""
    objects = model.objects.bulk_create([obj for obj, _ in rows])
    for obj, (_, when) in zip(objects, rows):
        for field in date_fields:
            setattr(obj, field, when)
    model.objects.bulk_update(objects, date_fields)
    return objects


class Command(BaseCommand):
    help = "Creates 30 days of demo orders, ratings, item views and searches."

    @transaction.atomic
    def handle(self, *args, **options):
        items = list(Item.objects.filter(is_active=True).select_related("brand").prefetch_related("sizes"))
        if not items:
            raise CommandError("Run seed_demo first: there are no items.")

        staff = self.staff_accounts()
        self.clear_activity(staff)
        rng = random.Random(2026)

        views, searches, orders, order_lines = [], [], [], []
        ordered = {person.pk: [] for person in staff}  # (item, when) pairs, used for ratings

        for days_ago in range(DAYS, -1, -1):
            for person in staff:
                for _ in range(rng.randint(0, 4)):
                    views.append((ItemView(user=person, item=rng.choice(items)), self.moment(days_ago, rng)))

                if rng.random() < 0.3:
                    term = rng.choice(SEARCH_TERMS)
                    matches = sum(1 for item in items if term in item.name.lower() or term in item.brand.name.lower())
                    searches.append((SearchQuery(user=person, term=term, results_count=matches), self.moment(days_ago, rng)))

                if rng.random() < 0.35:
                    when = self.moment(days_ago, rng)
                    lines = []
                    for item in rng.sample(items, rng.randint(1, 3)):
                        sizes = [size.name for size in item.sizes.all()]
                        lines.append(
                            OrderItem(
                                item=item,
                                size=rng.choice(sizes) if sizes else "",
                                quantity=rng.randint(1, 5),
                                unit_price=item.price,
                            )
                        )
                        ordered[person.pk].append((item, when))
                    total = sum(line.unit_price * line.quantity for line in lines)
                    orders.append((Order(user=person, total=total), when))
                    order_lines.append(lines)

        saved_orders = save_with_dates(Order, orders, ["created_at"])
        for order, lines in zip(saved_orders, order_lines):
            for line in lines:
                line.order = order
        OrderItem.objects.bulk_create([line for lines in order_lines for line in lines])

        save_with_dates(ItemView, views, ["viewed_at"])
        save_with_dates(SearchQuery, searches, ["created_at"])
        ratings = self.make_ratings(staff, ordered, rng)
        save_with_dates(Rating, ratings, ["created_at", "updated_at"])

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(orders)} orders, {len(ratings)} ratings, {len(views)} item views "
                f"and {len(searches)} searches over the last {DAYS} days."
            )
        )

    def staff_accounts(self):
        """demo_staff plus the extra staff accounts, which are created if missing."""
        demo_staff = User.objects.filter(username="demo_staff").first()
        if demo_staff is None:
            raise CommandError("Run seed_users first: demo_staff doesn't exist.")

        group, _ = Group.objects.get_or_create(name=STAFF_GROUP)
        accounts = [demo_staff]
        for username, first_name, last_name, club_slug in EXTRA_STAFF:
            person, created = User.objects.get_or_create(username=username)
            if created:
                person.set_unusable_password()  # data only: nobody can log in as them
            person.first_name = first_name
            person.last_name = last_name
            person.club = Team.objects.filter(slug=club_slug).first()
            person.save()
            person.groups.add(group)
            accounts.append(person)
        return accounts

    def clear_activity(self, staff):
        """Removes these accounts' previous activity, so running the command twice
        doesn't double the numbers."""
        Order.objects.filter(user__in=staff).delete()
        Rating.objects.filter(user__in=staff).delete()
        ItemView.objects.filter(user__in=staff).delete()
        SearchQuery.objects.filter(user__in=staff).delete()

    @staticmethod
    def moment(days_ago, rng):
        """A random time between 08:00 and 21:59, `days_ago` days back, never in the future."""
        now = timezone.now()
        day = timezone.localtime(now) - timedelta(days=days_ago)
        when = day.replace(hour=rng.randint(8, 21), minute=rng.randint(0, 59), second=0, microsecond=0)
        return min(when, now)

    @staticmethod
    def make_ratings(staff, ordered, rng):
        """Each staff member rates about 60% of the different items they ordered,
        mostly 4 or 5 stars, sometimes with a short review, 1 to 3 days after ordering."""
        ratings = []
        now = timezone.now()
        for person in staff:
            first_orders = {}
            for item, when in ordered[person.pk]:
                first_orders.setdefault(item.pk, (item, when))
            for item, when in first_orders.values():
                if rng.random() < 0.6:
                    stars = rng.choices([5, 4, 3, 2], weights=[40, 35, 18, 7])[0]
                    review = REVIEWS[stars] if rng.random() < 0.5 else ""
                    rated_at = min(when + timedelta(days=rng.randint(1, 3)), now)
                    ratings.append((Rating(user=person, item=item, stars=stars, review=review), rated_at))
        return ratings