"""The shopping cart, kept in the session instead of a database table.

The session stores a dictionary such as {"12|M": 3, "5|": 1}: each key is an item's id
plus the chosen size, each value is the quantity. The same item in two sizes is two lines.
"""

from decimal import Decimal

from catalogue.models import Item

SESSION_KEY = "cart"


class Cart:
    """Wraps the session so views can add, change, remove and list cart lines."""

    def __init__(self, request):
        self.session = request.session
        self.lines = self.session.get(SESSION_KEY, {})

    @staticmethod
    def make_key(item_id, size):
        """'12' and 'M' -> '12|M'. Items without sizes get '12|'."""
        return f"{item_id}|{size}"

    def add(self, item, size="", quantity=1):
        """Adds a quantity of an item in a size, on top of what is already in the cart."""
        key = self.make_key(item.pk, size)
        self.lines[key] = self.lines.get(key, 0) + quantity
        self.save()

    def set_quantity(self, key, quantity):
        """Changes a line's quantity; 0 removes the line. Unknown keys are ignored."""
        if key not in self.lines:
            return
        if quantity > 0:
            self.lines[key] = quantity
        else:
            self.lines.pop(key, None)
        self.save()

    def remove(self, key):
        self.lines.pop(key, None)
        self.save()

    def clear(self):
        self.lines = {}
        self.save()

    def save(self):
        """Writes the lines back into the session so they survive to the next page."""
        self.session[SESSION_KEY] = self.lines
        self.session.modified = True

    def __iter__(self):
        """Gives one dictionary per line, with the item fetched from the database.
        Items hidden or deleted since they were added are skipped."""
        ids = [int(key.split("|")[0]) for key in self.lines]
        items = Item.objects.filter(pk__in=ids, is_active=True).in_bulk()

        for key, quantity in self.lines.items():
            item_id, size = key.split("|", 1)
            item = items.get(int(item_id))
            if item is None:
                continue
            yield {
                "key": key,
                "item": item,
                "size": size,
                "quantity": quantity,
                "line_total": item.price * quantity,
            }

    def __len__(self):
        """Total number of pieces in the cart, shown next to the cart icon."""
        return sum(self.lines.values())

    def total(self):
        """Price of everything in the cart, at today's prices."""
        return sum((line["line_total"] for line in self), Decimal("0"))