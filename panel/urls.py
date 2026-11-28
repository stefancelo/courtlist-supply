from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
    path("items/", views.ItemList.as_view(), name="items"),
    path("items/add/", views.ItemCreate.as_view(), name="item_add"),
    path("items/<int:pk>/edit/", views.ItemUpdate.as_view(), name="item_edit"),
    path("items/<int:pk>/delete/", views.ItemDelete.as_view(), name="item_delete"),
    path("categories/", views.CategoryList.as_view(), name="categories"),
    path("categories/add/", views.CategoryCreate.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", views.CategoryUpdate.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.CategoryDelete.as_view(), name="category_delete"),
    path("brands/", views.BrandList.as_view(), name="brands"),
    path("brands/add/", views.BrandCreate.as_view(), name="brand_add"),
    path("brands/<int:pk>/edit/", views.BrandUpdate.as_view(), name="brand_edit"),
    path("brands/<int:pk>/delete/", views.BrandDelete.as_view(), name="brand_delete"),
    path("users/", views.UserList.as_view(), name="users"),
    path("users/<int:pk>/update/", views.UserUpdate.as_view(), name="user_update"),
    path("analytics/", views.AnalyticsView.as_view(), name="analytics"),
    path("analytics/data/", views.AnalyticsData.as_view(), name="analytics_data"),
]