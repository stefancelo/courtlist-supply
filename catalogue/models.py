from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """A catalogue category. A category with a parent is a sub-category,
    e.g. "Balls" inside "Game equipment"."""

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse("catalogue:category", args=[self.slug])


class Brand(models.Model):
    """The manufacturer of an item, e.g. Molten. Used for filtering and search."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Size(models.Model):
    """A size an item comes in, e.g. M or Size 7.
    sort_order keeps sizes in a logical order (S, M, L) instead of alphabetical."""

    name = models.CharField(max_length=20, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    """A product in the catalogue, always placed in a sub-category."""

    class Colour(models.TextChoices):
        BLACK = "black", "Black"
        WHITE = "white", "White"
        ORANGE = "orange", "Orange"
        NAVY = "navy", "Navy"
        RED = "red", "Red"
        GREY = "grey", "Grey"
        MULTI = "multi", "Multicolour"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="items")
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    colour = models.CharField(max_length=20, choices=Colour.choices)
    sizes = models.ManyToManyField(Size, blank=True, related_name="items")
    image = models.ImageField(upload_to="items/")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalogue:item_detail", args=[self.slug])
    
    

class SearchQuery(models.Model):
    """One search typed into the catalogue. Feeds the "most searched terms" chart
    on the analytics dashboard and the recommender."""

    term = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="searches",
    )
    results_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "search queries"

    def __str__(self):
        return self.term



class Rating(models.Model):
    """A staff member's star rating (1 to 5) and optional short review of an item.
    Each user rates an item once; rating again updates the same row."""

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    stars = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["item", "user"], name="one_rating_per_user_per_item"),
        ]

    def __str__(self):
        return f"{self.user} rated {self.item}: {self.stars}/5"


class ItemView(models.Model):
    """One visit by a user to an item's page. Feeds "recently viewed" on the dashboard,
    the recommender and the "most viewed" analytics."""

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="item_views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.user} viewed {self.item}"