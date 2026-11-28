from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from accounts.models import User
from accounts.roles import STAFF_GROUP, AdminRequiredMixin
from catalogue.models import Brand, Category, Item
from orders.models import Order

from .analytics import build_analytics
from .forms import AnalyticsFilterForm, BrandForm, CategoryForm, ItemForm


# ---------- Shared building blocks ----------


class PanelFormView(AdminRequiredMixin, SuccessMessageMixin):
    """Shared by every add and edit page: admins only, one form template, and a green
    notice after saving. Each page only sets its model, form, noun and list page."""

    template_name = "panel/form.html"
    success_message = "%(name)s was saved."
    noun = ""


class PanelDeleteView(AdminRequiredMixin, DeleteView):
    """Shared delete page: asks for confirmation, then deletes. If other records still
    use the row (PROTECT), nothing is deleted and the admin is told what to do instead."""

    template_name = "panel/confirm_delete.html"
    noun = ""
    protected_hint = ""

    def form_valid(self, form):
        name = str(self.object)
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, f"{name} can't be deleted because other records still use it. {self.protected_hint}")
        else:
            messages.success(self.request, f"{name} was deleted.")
        return redirect(self.success_url)


# ---------- Overview ----------


class OverviewView(AdminRequiredMixin, TemplateView):
    """The panel's start page: how many of everything there is, with links."""

    template_name = "panel/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["counts"] = [
            ("Items", Item.objects.count(), "panel:items"),
            ("Categories", Category.objects.count(), "panel:categories"),
            ("Brands", Brand.objects.count(), "panel:brands"),
            ("Users", User.objects.count(), "panel:users"),
            ("Orders", Order.objects.count(), "panel:analytics"),
        ]
        return context


# ---------- Items ----------


class ItemList(AdminRequiredMixin, ListView):
    """Every item, hidden ones included, with a name search."""

    template_name = "panel/item_list.html"

    def get_queryset(self):
        items = Item.objects.select_related("category__parent", "brand")
        query = self.request.GET.get("q", "").strip()
        if query:
            items = items.filter(name__icontains=query)
        return items


class ItemCreate(PanelFormView, CreateView):
    model = Item
    form_class = ItemForm
    noun = "item"
    success_url = reverse_lazy("panel:items")


class ItemUpdate(PanelFormView, UpdateView):
    model = Item
    form_class = ItemForm
    noun = "item"
    success_url = reverse_lazy("panel:items")


class ItemDelete(PanelDeleteView):
    model = Item
    noun = "item"
    success_url = reverse_lazy("panel:items")
    protected_hint = "It appears in past orders. Untick \"Is active\" on its edit page to hide it instead."


# ---------- Categories ----------


class CategoryList(AdminRequiredMixin, ListView):
    """Top-level categories first, then sub-categories, each with its number of items."""

    template_name = "panel/category_list.html"

    def get_queryset(self):
        return (
            Category.objects.select_related("parent")
            .annotate(item_count=Count("items"))
            .order_by("parent__name", "name")
        )


class CategoryCreate(PanelFormView, CreateView):
    model = Category
    form_class = CategoryForm
    noun = "category"
    success_url = reverse_lazy("panel:categories")


class CategoryUpdate(PanelFormView, UpdateView):
    model = Category
    form_class = CategoryForm
    noun = "category"
    success_url = reverse_lazy("panel:categories")


class CategoryDelete(PanelDeleteView):
    model = Category
    noun = "category"
    success_url = reverse_lazy("panel:categories")
    protected_hint = "Move or delete its items first."


# ---------- Brands ----------


class BrandList(AdminRequiredMixin, ListView):
    template_name = "panel/brand_list.html"

    def get_queryset(self):
        return Brand.objects.annotate(item_count=Count("items"))


class BrandCreate(PanelFormView, CreateView):
    model = Brand
    form_class = BrandForm
    noun = "brand"
    success_url = reverse_lazy("panel:brands")


class BrandUpdate(PanelFormView, UpdateView):
    model = Brand
    form_class = BrandForm
    noun = "brand"
    success_url = reverse_lazy("panel:brands")


class BrandDelete(PanelDeleteView):
    model = Brand
    noun = "brand"
    success_url = reverse_lazy("panel:brands")
    protected_hint = "Give its items another brand first."


# ---------- Users ----------


class UserList(AdminRequiredMixin, ListView):
    """Every account with its role and club."""

    template_name = "panel/user_list.html"

    def get_queryset(self):
        return (
            User.objects.select_related("club")
            .annotate(in_staff_group=Count("groups", filter=Q(groups__name=STAFF_GROUP)))
            .order_by("username")
        )


class UserUpdate(AdminRequiredMixin, View):
    """Changes a user's role or access from the Users list (POST only).
    Admin accounts are left alone, so no admin can lock themselves out."""

    def post(self, request, pk):
        person = get_object_or_404(User, pk=pk)
        if person.is_superuser:
            messages.error(request, "Admin accounts can't be changed here.")
            return redirect("panel:users")

        staff_group, _ = Group.objects.get_or_create(name=STAFF_GROUP)
        action = request.POST.get("action")

        if action == "make_staff":
            person.groups.add(staff_group)
            messages.success(request, f"{person.username} is now CourtList staff.")
        elif action == "make_fan":
            person.groups.remove(staff_group)
            messages.success(request, f"{person.username} is now a fan.")
        elif action in ("deactivate", "activate"):
            person.is_active = action == "activate"
            person.save(update_fields=["is_active"])
            state = "reactivated" if person.is_active else "deactivated"
            messages.success(request, f"{person.username} was {state}.")
        else:
            messages.error(request, "Unknown action.")

        return redirect("panel:users")




# ---------- Analytics ----------


def default_period():
    """The last 30 days, today included."""
    end = timezone.localdate()
    return {"start": end - timedelta(days=29), "end": end}


class AnalyticsView(AdminRequiredMixin, TemplateView):
    """The analytics page: the filters and empty charts. The numbers arrive from
    AnalyticsData through fetch, so changing a filter doesn't reload the page."""

    template_name = "panel/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = AnalyticsFilterForm(initial=default_period())
        return context


class AnalyticsData(AdminRequiredMixin, View):
    """JSON endpoint for the charts: reads the filters from the address and returns
    every statistic, or the form's errors with status 400."""

    def get(self, request):
        form = AnalyticsFilterForm(request.GET or default_period())
        if not form.is_valid():
            messages_list = [str(error) for errors in form.errors.values() for error in errors]
            return JsonResponse({"errors": messages_list}, status=400)
        data = form.cleaned_data
        return JsonResponse(build_analytics(data["start"], data["end"], data["category"]))