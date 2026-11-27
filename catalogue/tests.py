from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from accounts.roles import STAFF_GROUP
from orders.models import Order, OrderItem

from .forms import ItemFilterForm
from .models import Brand, Category, Item, ItemView, Rating, SearchQuery
from .recommender import recommend_for


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


    def order_ball(self):
        """Gives the staff user a past order containing the ball, so they may rate it."""
        order = Order.objects.create(user=self.staff, total="99.00")
        OrderItem.objects.create(order=order, item=self.ball, quantity=1, unit_price="99.00")

    def test_rating_without_ordering_is_refused(self):
        url = reverse("catalogue:rate", args=[self.ball.pk])
        response = self.client.post(url, {"stars": 5}, headers={"X-Requested-With": "fetch"})

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Rating.objects.exists())

    def test_rating_by_fetch_is_saved_once_per_user(self):
        self.order_ball()
        url = reverse("catalogue:rate", args=[self.ball.pk])
        fetch = {"X-Requested-With": "fetch"}
        self.client.post(url, {"stars": 4, "review": "Great grip."}, headers=fetch)
        response = self.client.post(url, {"stars": 2}, headers=fetch)

        self.assertTrue(response.json()["ok"])
        self.assertEqual(Rating.objects.get().stars, 2)

    def test_invalid_rating_is_rejected(self):
        self.order_ball()
        url = reverse("catalogue:rate", args=[self.ball.pk])
        response = self.client.post(url, {"stars": 9}, headers={"X-Requested-With": "fetch"})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Rating.objects.exists())

    def test_opening_an_item_records_a_view(self):
        self.client.get(reverse("catalogue:item_detail", args=["test-ball"]))
        self.assertEqual(ItemView.objects.filter(user=self.staff).count(), 1)
        
        


class ItemFilterFormTests(TestCase):
    """Checks the advanced filter form's own validation."""

    def test_min_price_above_max_price_is_rejected(self):
        form = ItemFilterForm({"min_price": "50", "max_price": "10"})
        self.assertFalse(form.is_valid())
        self.assertIn("max_price", form.errors)




class RecommenderTests(TestCase):
    """Checks that recommendations follow what the user viewed and leave out what they ordered."""

    @classmethod
    def setUpTestData(cls):
        balls = Category.objects.create(name="Balls", slug="balls")
        towels = Category.objects.create(name="Towels", slug="towels")
        brand = Brand.objects.create(name="Molten", slug="molten")

        def make_item(name, slug, category):
            return Item.objects.create(
                name=name,
                slug=slug,
                category=category,
                brand=brand,
                description="Test item.",
                price="10.00",
                colour="orange",
                image="items/test.png",
                stock=5,
            )

        cls.ball_a = make_item("Ball A", "ball-a", balls)
        cls.ball_b = make_item("Ball B", "ball-b", balls)
        cls.towel = make_item("Towel", "towel", towels)
        cls.user = User.objects.create_user(username="viewer", password="Test-pass-2026")

    def test_viewed_category_comes_first(self):
        ItemView.objects.create(item=self.ball_a, user=self.user)
        picks = recommend_for(self.user, exclude=self.ball_a)

        self.assertEqual(picks[0], self.ball_b)

    def test_ordered_items_are_left_out(self):
        order = Order.objects.create(user=self.user, total="10.00")
        OrderItem.objects.create(order=order, item=self.ball_b, quantity=1, unit_price="10.00")

        self.assertNotIn(self.ball_b, recommend_for(self.user))