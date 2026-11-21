from django.test import TestCase
from django.urls import reverse

from .models import Brand, Category, Item


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

    def test_parent_category_includes_subcategory_items(self):
        response = self.client.get(reverse("catalogue:category", args=["game-equipment"]))
        self.assertContains(response, "Test ball")

    def test_hidden_item_page_returns_404(self):
        self.ball.is_active = False
        self.ball.save()
        response = self.client.get(reverse("catalogue:item_detail", args=["test-ball"]))
        self.assertEqual(response.status_code, 404)