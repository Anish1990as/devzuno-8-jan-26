from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import (
    PricingPlan, PricingCategory,
    PortfolioItem, Testimonial, Review,
    HomeService, WhyDevzuno, HowWeWork, HomePortfolio
)

from projects.models import Project
from .forms import ContactForm


# -----------------------------
# HOME
# -----------------------------
def home(request):
    services = HomeService.objects.filter(is_active=True)
    why_points = WhyDevzuno.objects.all()
    work_steps = HowWeWork.objects.all()
    portfolio_items = HomePortfolio.objects.filter(is_active=True)

    return render(request, "core/home.html", {
        "services": services,
        "why_points": why_points,
        "work_steps": work_steps,
        "portfolio_items": portfolio_items,
    })


# -----------------------------
# PRICING (Category wise)
# URL: /pricing/?cat=blog
# -----------------------------
def pricing(request):
    cat_slug = request.GET.get("cat")

    categories = PricingCategory.objects.filter(is_active=True).order_by("sort_order", "name")

    # pick active category
    if cat_slug:
        active_cat = categories.filter(slug=cat_slug).first()
    else:
        active_cat = categories.first()

    # plans filter by category
    if active_cat:
        plans = PricingPlan.objects.filter(category=active_cat, is_active=True).order_by("-highlight", "price")
    else:
        plans = PricingPlan.objects.filter(category__isnull=True, is_active=True).order_by("-highlight", "price")

    # ✅ CUSTOM PLAN LAST (slug = Custom)
    plans = list(plans)
    plans = sorted(plans, key=lambda p: (p.slug.lower() == "custom"))

    return render(request, "core/pricing.html", {
        "categories": categories,
        "active_cat": active_cat,
        "plans": plans
    })


# -----------------------------
# ORDER PAGE ✅
# URL: /order/?plan=<slug>
# -----------------------------
@login_required(login_url='/client/login/')
def order(request):
    plan_slug = request.GET.get("plan")

    plan = None
    if plan_slug:
        plan = PricingPlan.objects.filter(slug=plan_slug, is_active=True).select_related("category").first()

    # If plan not found, show message
    if plan_slug and not plan:
        messages.error(request, "Plan not found or inactive. Please choose a valid plan.")
        return redirect("/pricing/")

    return render(request, "core/order.html", {
        "plan": plan
    })


# -----------------------------
# PORTFOLIO
# -----------------------------
def portfolio(request):
    items = PortfolioItem.objects.all()[:12]
    return render(request, "core/portfolio.html", {"items": items})


# -----------------------------
# REVIEWS
# -----------------------------
def reviews(request):
    reviews_qs = Review.objects.filter(is_approved=True).select_related("project", "user")
    testimonials = Testimonial.objects.all()

    avg = None
    if reviews_qs.exists():
        avg = round(sum(r.rating for r in reviews_qs) / reviews_qs.count(), 1)

    return render(request, "core/reviews.html", {
        "reviews": reviews_qs,
        "testimonials": testimonials,
        "avg": avg,
        "count": reviews_qs.count()
    })


# -----------------------------
# NEW REVIEW
# -----------------------------
@login_required(login_url='/client/login/')
def review_new(request, project_id):
    project = get_object_or_404(Project, pk=project_id, client=request.user)

    if project.status != 'done':
        messages.error(request, "You can rate only after the project is delivered.")
        return redirect('/projects/')

    if Review.objects.filter(user=request.user, project=project).exists():
        messages.info(request, "You have already submitted a review for this project.")
        return redirect('/projects/')

    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        comment = (request.POST.get("comment") or "").strip()

        if rating < 1 or rating > 5:
            messages.error(request, "Please choose a rating between 1 and 5.")
        else:
            Review.objects.create(
                user=request.user,
                project=project,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Thanks! Your review has been submitted ✅")
            return redirect('/reviews/')

    return render(request, "core/review_form.html", {"project": project})


# -----------------------------
# CONTACT
# -----------------------------
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Thanks! Your message has been submitted. We'll contact you soon ✅")
            return redirect("/contact/")
        else:
            messages.error(request, "Please fix the errors and try again ❌")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})




# -----------------------------
# DASHBOARD
# -----------------------------
def dashboard(request):
    categories = PricingCategory.objects.filter(is_active=True).order_by("sort_order", "name")
    return render(request, "core/dashboard.html", {"categories": categories})


# -----------------------------
# ABOUT
# -----------------------------
def about(request):
    return render(request, "core/about.html")


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def services(request):
    return render(request, "core/services.html")
