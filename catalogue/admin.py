from django.contrib import admin

from .models import Brand, Category, Item, ItemView, Rating, SearchQuery, Size


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]
    list_filter = ["parent"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order"]
    list_editable = ["sort_order"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "brand", "price", "stock", "is_active"]
    list_filter = ["category", "brand", "colour", "is_active"]
    search_fields = ["name", "brand__name"]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal = ["sizes"]
    

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["term", "user", "results_count", "created_at"]
    list_filter = ["created_at"]

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["item", "user", "stars", "updated_at"]
    list_filter = ["stars"]
    search_fields = ["item__name", "user__username", "review"]


@admin.register(ItemView)
class ItemViewAdmin(admin.ModelAdmin):
    list_display = ["item", "user", "viewed_at"]
    list_filter = ["viewed_at"]