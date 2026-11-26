from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.roles import staff_required
from catalogue.models import Item

from .cart import Cart
from .models import Order, OrderItem


def parse_quantity(value):
    """Turns the quantity sent by a form into a whole number; anything else counts as 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@staff_required
def cart_detail(request):
    """The cart page: every line with its quantity and price, and the total."""
    cart = Cart(request)
    return render(request, "orders/cart.html", {"lines": list(cart), "total": cart.total()})


@staff_required
@require_POST
def cart_add(request, item_id):
    """Adds an item to the cart from its page, after checking the size, quantity and stock."""
    item = get_object_or_404(Item, pk=item_id, is_active=True)
    valid_sizes = list(item.sizes.values_list("name", flat=True))
    size = request.POST.get("size", "") if valid_sizes else ""
    quantity = parse_quantity(request.POST.get("quantity"))

    if valid_sizes and size not in valid_sizes:
        messages.error(request, "Choose a size first.")
    elif quantity < 1:
        messages.error(request, "Enter a quantity of at least 1.")
    elif quantity > item.stock:
        messages.error(request, f"Only {item.stock} in stock.")
    else:
        Cart(request).add(item, size, quantity)
        messages.success(request, f"Added {quantity} x {item.name} to your cart.")

    return redirect(item)


def find_line(cart, key):
    """Returns the cart line with this key, or None."""
    return next((line for line in cart if line["key"] == key), None)


@staff_required
@require_POST
def cart_update(request):
    """Changes a line's quantity on the cart page; 0 (the Remove button) removes it.
    Called by fetch from cart.js, it answers with JSON so the page updates instantly;
    as a normal form (JavaScript off) it redirects back to the cart."""
    cart = Cart(request)
    key = request.POST.get("key", "")
    quantity = parse_quantity(request.POST.get("quantity"))

    # Never allow more than the stock, whatever the browser sent
    line = find_line(cart, key)
    if line:
        quantity = min(quantity, line["item"].stock)
    cart.set_quantity(key, quantity)

    if request.headers.get("X-Requested-With") == "fetch":
        line = find_line(cart, key)
        return JsonResponse(
            {
                "quantity": line["quantity"] if line else 0,
                "line_total": str(line["line_total"]) if line else "0.00",
                "total": str(cart.total()),
                "count": len(cart),
            }
        )
    return redirect("orders:cart")



@staff_required
@require_POST
def checkout(request):
    """Turns the cart into an order. Everything happens in one transaction: if any item
    no longer has enough stock, nothing is saved and the user is told which item."""
    cart = Cart(request)
    lines = list(cart)
    if not lines:
        messages.error(request, "Your cart is empty.")
        return redirect("orders:cart")

    # How many pieces of each item the cart needs (one item can be in several sizes)
    needed = {}
    for line in lines:
        needed[line["item"].pk] = needed.get(line["item"].pk, 0) + line["quantity"]

    with transaction.atomic():
        items = Item.objects.select_for_update().in_bulk(list(needed))
        short = [items[pk].name for pk, quantity in needed.items() if items[pk].stock < quantity]
        if short:
            messages.error(request, f"Not enough stock for: {', '.join(short)}. Please lower the quantity.")
            return redirect("orders:cart")

        order = Order.objects.create(
            user=request.user,
            total=sum(line["line_total"] for line in lines),
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    item=line["item"],
                    size=line["size"],
                    quantity=line["quantity"],
                    unit_price=line["item"].price,
                )
                for line in lines
            ]
        )
        for pk, quantity in needed.items():
            Item.objects.filter(pk=pk).update(stock=F("stock") - quantity)

    cart.clear()
    messages.success(request, f"Order #{order.pk} placed. Thank you!")
    return redirect("orders:detail", pk=order.pk)


@staff_required
def order_list(request):
    """The logged-in staff member's own orders, newest first."""
    orders = request.user.orders.prefetch_related("lines")
    return render(request, "orders/order_list.html", {"orders": orders})


@staff_required
def order_detail(request, pk):
    """One of the user's own orders. Someone else's order number gives 404."""
    order = get_object_or_404(Order.objects.prefetch_related("lines__item"), pk=pk, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


@staff_required
@require_POST
def reorder(request, pk):
    """Restock in one click: puts every line of a past order back in the cart.
    Items no longer sold are skipped; stock is checked again at checkout."""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    cart = Cart(request)
    added = 0
    for line in order.lines.select_related("item"):
        if line.item.is_active:
            cart.add(line.item, line.size, line.quantity)
            added += 1

    if added:
        messages.success(request, f"The items from order #{order.pk} are back in your cart.")
    else:
        messages.error(request, "None of the items from that order are sold any more.")
    return redirect("orders:cart")