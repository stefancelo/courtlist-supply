from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Shows an order's lines inside the order's own admin page."""

    model = OrderItem
    extra = 0
    readonly_fields = ["item", "size", "quantity", "unit_price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at", "total"]
    list_filter = ["created_at"]
    inlines = [OrderItemInline]