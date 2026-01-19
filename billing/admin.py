# billing/admin.py
from django.contrib import admin
from .models import ServiceCategory, ServicePlan, ServiceSubscription, Order, Invoice
from .models import Coupon

# -------- ServiceCategory --------
@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


# -------- ServicePlan --------
@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug", "price_monthly", "price_yearly", "is_active", "sort")
    list_filter = ("is_active", "category")
    search_fields = ("name", "slug", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("category__name", "sort", "price_monthly")
    autocomplete_fields = ("category",)


# -------- ServiceSubscription --------
@admin.register(ServiceSubscription)
class ServiceSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "plan", "status", "billing_period", "started_at", "renews_at", "cancel_at_period_end")
    list_filter = ("status", "billing_period", "plan", "started_at")
    search_fields = ("user__username", "user__email", "plan__name")
    ordering = ("-started_at",)
    autocomplete_fields = ("user", "plan")

    actions = ["mark_active", "mark_pending", "mark_canceled", "mark_expired"]

    @admin.action(description="Mark selected as Active")
    def mark_active(self, request, qs):
        qs.update(status="active")

    @admin.action(description="Mark selected as Pending")
    def mark_pending(self, request, qs):
        qs.update(status="pending")

    @admin.action(description="Mark selected as Canceled")
    def mark_canceled(self, request, qs):
        qs.update(status="canceled")

    @admin.action(description="Mark selected as Expired")
    def mark_expired(self, request, qs):
        qs.update(status="expired")


# -------- Invoice Inline on Order --------
class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    fields = ("amount", "status", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


# -------- Order --------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "package", "created_at", "invoice_count", "total_billed")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "package")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    autocomplete_fields = ("user",)
    inlines = [InvoiceInline]

    def invoice_count(self, obj):
        return obj.invoices.count()
    invoice_count.short_description = "Invoices"

    def total_billed(self, obj):
        # safe sum; sqlite ok
        return sum(i.amount for i in obj.invoices.all())
    total_billed.short_description = "Total Billed"


# -------- Invoice --------
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "user_display", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "order__package", "order__user__username", "order__user__email")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    autocomplete_fields = ("order",)

    def user_display(self, obj):
        return getattr(obj.order.user, "username", str(obj.order.user))
    user_display.short_description = "User"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    list_filter = ('is_active', 'discount_type')
