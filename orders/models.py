from django.conf import settings
from django.db import models


class Order(models.Model):
    """One checkout by a staff member. The total is stored so it never changes later."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"


class OrderItem(models.Model):
    """One line of an order. The price is copied at checkout, so later price
    changes in the shop never change what was paid."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey("catalogue.Item", on_delete=models.PROTECT, related_name="order_lines")
    size = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.item}"

    @property
    def line_total(self):
        """Price of this line: unit price times quantity."""
        return self.unit_price * self.quantity