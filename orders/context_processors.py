from accounts.roles import is_courtlist_staff

from .cart import Cart


def cart(request):
    """Adds the number of pieces in the cart to every template, for the navbar badge.
    Only staff have a cart, so everyone else gets nothing."""
    if not is_courtlist_staff(request.user):
        return {}
    return {"cart_count": len(Cart(request))}