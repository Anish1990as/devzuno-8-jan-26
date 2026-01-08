
from django.contrib import admin
from .models import PricingPlan, PricingCategory, PortfolioItem, Testimonial, Review
from django.utils.html import format_html
from .models import ContactMessage
from .models import Profile 
from .models import HomeService, WhyDevzuno, HowWeWork, HomePortfolio


admin.site.site_header = "Devzuno Admin"
admin.site.site_title  = "Devzuno Admin"
admin.site.index_title = "Control Panel"


@admin.register(HomeService)
class HomeServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(WhyDevzuno)
class WhyDevzunoAdmin(admin.ModelAdmin):
    list_display = ("point", "order")
    list_editable = ("order",)


@admin.register(HowWeWork)
class HowWeWorkAdmin(admin.ModelAdmin):
    list_display = ("title", "step_number")
    list_editable = ("step_number",)


@admin.register(HomePortfolio)
class HomePortfolioAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")

@admin.register(PricingCategory)
class PricingCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "sort_order", "is_active")
    list_editable = ("icon", "sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    ordering = ("sort_order", "name")


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_text", "category", "highlight")
    list_filter = ("category", "highlight")
    search_fields = ("name",)
    autocomplete_fields = ("category",)



@admin.register(PortfolioItem)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "project_link")
    search_fields = ("title",)

    def thumb(self, obj):
        # Small preview if uploaded image exists
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;object-fit:cover;">', obj.image.url)
        return "—"
    thumb.short_description = "Image"

 
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author",)
    search_fields = ("author",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("project__name", "user__username", "comment")  # 👈 added for autocomplete
    autocomplete_fields = ("project", "user")  # works now
    ordering = ("-created_at",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "full_phone", "website_type", "created_at", "resolved")
    list_filter  = ("website_type", "resolved", "created_at")
    search_fields = ("name", "email", "country_code", "phone", "full_phone", "location", "pincode", "message")
    readonly_fields = ("created_at", "full_phone")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "country_code", "phone", "city", "country")  # ← no updated_at
    search_fields = ("user__username", "user__email", "phone", "city", "country")
    list_filter   = ()       # make sure updated_at not here
    ordering      = ("user",)  # make sure updated_at not here
    readonly_fields = ()     # make sure updated_at not here