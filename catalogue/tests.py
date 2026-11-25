from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from accounts.roles import STAFF_GROUP

from .forms import ItemFilterForm
from .models import Brand, Category, Item, SearchQuery


class CategoryModelTests(TestCase):
    """Checks that sub-categories are linked to their parent and named after it."""

    def test_subcategory_shows_parent_name(self):
        parent = Category.objects.create(name="Game equipment", slug="game-equipment")
        child = Category.objects.create(name="Balls", slug="balls", parent=parent)

        self.assertEqual(str(child), "Game equipment > Balls")
        self.assertEqual(list(parent.children.all()), [child])
        

class CatalogueViewTests(TestCase):
    """Checks that the catalogue pages show the right items."""

    @classmethod
    def setUpTestData(cls):
        parent = Category.objects.create(name="Game equipment", slug="game-equipment")
        balls = Category.objects.create(name="Balls", slug="balls", parent=parent)
        brand = Brand.objects.create(name="Molten", slug="molten")
        cls.ball = Item.objects.create(
            name="Test ball",
            slug="test-ball",
            category=balls,
            brand=brand,
            description="A ball for testing.",
            price="99.00",
            colour="orange",
            image="items/test.png",
            stock=5,
        )
        cls.staff = User.objects.create_user(username="staff", password="Test-pass-2026")
        cls.staff.groups.add(Group.objects.create(name=STAFF_GROUP))
        cls.fan = User.objects.create_user(username="fan", password="Test-pass-2026")

    def setUp(self):
        # Every test starts logged in as staff, because the shop is staff-only
        self.client.force_login(self.staff)

    def test_visitor_is_sent_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("catalogue:item_list"))
        login_url = reverse("accounts:login")
        self.assertRedirects(response, f"{login_url}?next={reverse('catalogue:item_list')}")

    def test_fan_is_forbidden(self):
        self.client.force_login(self.fan)
        response = self.client.get(reverse("catalogue:item_list"))
        self.assertEqual(response.status_code, 403)

    def test_parent_category_includes_subcategory_items(self):
        response = self.client.get(reverse("catalogue:category", args=["game-equipment"]))
        self.assertContains(response, "Test ball")

    def test_hidden_item_page_returns_404(self):
        self.ball.is_active = False
        self.ball.save()
        response = self.client.get(reverse("catalogue:item_detail", args=["test-ball"]))
        self.assertEqual(response.status_code, 404)
        
    
    def test_search_matches_brand_and_is_saved(self):
        response = self.client.get(reverse("catalogue:item_list"), {"q": "Molten"})
        self.assertContains(response, "Test ball")
        self.assertEqual(SearchQuery.objects.get().term, "molten")
        
        


class ItemFilterFormTests(TestCase):
    """Checks the advanced filter form's own validation."""

    def test_min_price_above_max_price_is_rejected(self):
        form = ItemFilterForm({"min_price": "50", "max_price": "10"})
        self.assertFalse(form.is_valid())
        self.assertIn("max_price", form.errors)