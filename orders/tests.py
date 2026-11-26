from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from accounts.roles import STAFF_GROUP
from catalogue.models import Brand, Category, Item

from .models import Order


class CheckoutTests(TestCase):
    """Checks checkout (order created, stock reduced), the stock safety check
    and that users can't open each other's orders."""

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Balls", slug="balls")
        brand = Brand.objects.create(name="Molten", slug="molten")
        cls.ball = Item.objects.create(
            name="Test ball",
            slug="test-ball",
            category=category,
            brand=brand,
            description="A ball for testing.",
            price="50.00",
            colour="orange",
            image="items/test.png",
            stock=3,
        )
        staff_group = Group.objects.create(name=STAFF_GROUP)
        cls.staff = User.objects.create_user(username="staff", password="Test-pass-2026")
        cls.staff.groups.add(staff_group)
        cls.other = User.objects.create_user(username="other", password="Test-pass-2026")
        cls.other.groups.add(staff_group)

    def setUp(self):
        self.client.force_login(self.staff)

    def add_to_cart(self, quantity):
        self.client.post(reverse("orders:cart_add", args=[self.ball.pk]), {"quantity": quantity})

    def test_checkout_creates_order_and_reduces_stock(self):
        self.add_to_cart(2)
        response = self.client.post(reverse("orders:checkout"))

        order = Order.objects.get()
        self.assertRedirects(response, reverse("orders:detail", args=[order.pk]))
        self.assertEqual(order.total, Decimal("100.00"))
        self.ball.refresh_from_db()
        self.assertEqual(self.ball.stock, 1)

    def test_checkout_is_refused_when_stock_ran_out(self):
        self.add_to_cart(2)
        Item.objects.filter(pk=self.ball.pk).update(stock=1)  # someone else bought one meanwhile
        self.client.post(reverse("orders:checkout"))

        self.assertFalse(Order.objects.exists())

    def test_other_users_order_gives_404(self):
        order = Order.objects.create(user=self.other, total="10.00")
        response = self.client.get(reverse("orders:detail", args=[order.pk]))

        self.assertEqual(response.status_code, 404)