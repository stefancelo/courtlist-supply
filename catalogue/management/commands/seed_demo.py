"""seed_demo: fills the database with the CourtList Supply demo catalogue.

Usage:  python manage.py seed_demo

Safe to run more than once: rows are matched by their slug or name and updated,
never duplicated. Every photo is placed on a white square, resized to 800 x 800
and saved as a compressed JPEG, so pages load fast whatever the original size.
"""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from PIL import Image

from catalogue.demo.data import CATEGORIES, ITEMS, SIZES
from catalogue.models import Brand, Category, Item, Size

# catalogue/management/commands/seed_demo.py -> parents[2] is the catalogue folder
IMAGES_DIR = Path(__file__).resolve().parents[2] / "demo" / "images"
IMAGE_SIZE = 800


def prepare_image(path):
    """Places a photo in the middle of a white square, resizes it to IMAGE_SIZE
    and returns it as a compressed JPEG file ready to save on an ImageField."""
    with Image.open(path) as photo:
        photo = photo.convert("RGBA")
        side = max(photo.size)
        square = Image.new("RGBA", (side, side), (255, 255, 255, 255))
        offset = ((side - photo.width) // 2, (side - photo.height) // 2)
        square.paste(photo, offset, photo)
        square = square.convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    square.save(buffer, format="JPEG", quality=82, optimize=True)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Creates the demo categories, brands, sizes and items with their photos."

    @transaction.atomic
    def handle(self, *args, **options):
        sizes = self.create_sizes()
        categories = self.create_categories()
        created = sum(self.create_item(data, sizes, categories) for data in ITEMS)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo catalogue ready: {len(categories)} categories, {created} items."
            )
        )

    def create_sizes(self):
        """Creates the sizes and returns them as a dictionary {name: Size}."""
        sizes = {}
        for name, sort_order in SIZES:
            size, _ = Size.objects.update_or_create(name=name, defaults={"sort_order": sort_order})
            sizes[name] = size
        return sizes

    def create_categories(self):
        """Creates the top categories and their sub-categories.
        Returns every category as a dictionary {slug: Category}."""
        categories = {}
        for top in CATEGORIES:
            parent, _ = Category.objects.update_or_create(
                slug=top["slug"],
                defaults={"name": top["name"], "description": top["description"], "parent": None},
            )
            categories[parent.slug] = parent

            for child in top["children"]:
                sub, _ = Category.objects.update_or_create(
                    slug=child["slug"],
                    defaults={"name": child["name"], "parent": parent},
                )
                categories[sub.slug] = sub
        return categories

    def create_item(self, data, sizes, categories):
        """Creates or updates one item with its photo.
        Returns True if the item was saved, False if its photo is missing."""
        photos = sorted(IMAGES_DIR.glob(f"{data['slug']}.*"))
        if not photos:
            self.stderr.write(
                self.style.WARNING(f"Skipped {data['name']}: no photo named {data['slug']}.*")
            )
            return False

        brand, _ = Brand.objects.get_or_create(
            name=data["brand"], defaults={"slug": slugify(data["brand"])}
        )
        item, _ = Item.objects.update_or_create(
            slug=data["slug"],
            defaults={
                "name": data["name"],
                "category": categories[data["category"]],
                "brand": brand,
                "description": data["description"],
                "price": data["price"],
                "colour": data["colour"],
                "stock": data["stock"],
                "is_active": True,
            },
        )

        # Replace the old photo file instead of piling up copies on every run
        if item.image:
            item.image.delete(save=False)
        item.image.save(f"{data['slug']}.jpg", prepare_image(photos[0]), save=True)

        item.sizes.set([sizes[name] for name in data["sizes"]])
        return True