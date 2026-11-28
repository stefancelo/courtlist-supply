from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from accounts.roles import STAFF_GROUP
from catalogue.models import Brand, Category, Item
from orders.models import Order, OrderItem


class PanelTests(TestCase):
    """Checks who can open the admin panel, and its main actions."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(username="boss", email="boss@example.com", password="Test-pass-2026")
        cls.staff = User.objects.create_user(username="staff", password="Test-pass-2026")
        cls.staff.groups.add(Group.objects.create(name=STAFF_GROUP))
        cls.fan = User.objects.create_user(username="fan", password="Test-pass-2026")

        cls.parent = Category.objects.create(name="Game equipment", slug="game-equipment")
        balls = Category.objects.create(name="Balls", slug="balls", parent=cls.parent)
        brand = Brand.objects.create(name="Molten", slug="molten")
        cls.item = Item.objects.create(
            name="Test ball",
            slug="test-ball",
            category=balls,
            brand=brand,
            description="A ball for testing.",
            price="50.00",
            colour="orange",
            image="items/test.png",
            stock=3,
        )

    def test_staff_cannot_open_panel(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("panel:overview"))
        self.assertEqual(response.status_code, 403)

    def test_admin_adds_category_with_slug_made_from_name(self):
        self.client.force_login(self.admin)
        data = {"name": "Score Boards", "slug": "", "parent": self.parent.pk, "description": ""}
        self.client.post(reverse("panel:category_add"), data)

        self.assertTrue(Category.objects.filter(slug="score-boards", parent=self.parent).exists())

    def test_ordered_item_is_protected_from_delete(self):
        order = Order.objects.create(user=self.staff, total="50.00")
        OrderItem.objects.create(order=order, item=self.item, quantity=1, unit_price="50.00")
        self.client.force_login(self.admin)
        self.client.post(reverse("panel:item_delete", args=[self.item.pk]))

        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())

    def test_admin_makes_fan_staff(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("panel:user_update", args=[self.fan.pk]), {"action": "make_staff"})

        self.assertTrue(self.fan.groups.filter(name=STAFF_GROUP).exists())


    def test_analytics_revenue_is_summed_by_the_database(self):
        order = Order.objects.create(user=self.staff, total="150.00")
        OrderItem.objects.create(order=order, item=self.item, quantity=3, unit_price="50.00")
        self.client.force_login(self.admin)
        data = self.client.get(reverse("panel:analytics_data")).json()

        self.assertEqual(data["totals"], {"orders": 1, "revenue": "150.00"})
        self.assertEqual(data["best_sellers"]["values"], [3])

    def test_analytics_rejects_reversed_dates(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("panel:analytics_data"), {"start": "2026-11-28", "end": "2026-11-01"})

        self.assertEqual(response.status_code, 400)

    def test_staff_cannot_read_analytics_data(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("panel:analytics_data"))

        self.assertEqual(response.status_code, 403)