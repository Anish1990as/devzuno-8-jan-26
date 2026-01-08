
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import PricingPlan, PortfolioItem, Testimonial, PricingCategory

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Review, Testimonial
from projects.models import Project
from .forms import ContactForm
from .models import HomeService, WhyDevzuno, HowWeWork, HomePortfolio


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

def pricing(request):
    plans = PricingPlan.objects.all().order_by('-highlight')
    return render(request, 'core/pricing.html', {'plans': plans})

def pricing(request):
    cat_slug = request.GET.get("cat")
    categories = PricingCategory.objects.filter(is_active=True).order_by("sort_order", "name")

    if cat_slug:
        active_cat = categories.filter(slug=cat_slug).first()
    else:
        active_cat = categories.first()

    if active_cat:
        plans = PricingPlan.objects.filter(category=active_cat).order_by('-highlight', 'name')
    else:
        plans = PricingPlan.objects.filter(category__isnull=True).order_by('-highlight', 'name')

    return render(request, 'core/pricing.html', {
        'categories': categories,
        'active_cat': active_cat,
        'plans': plans
    })


def portfolio(request):
    items = PortfolioItem.objects.all()[:12]
    return render(request, 'core/portfolio.html', {'items': items})

def reviews(request):
    reviews = Review.objects.filter(is_approved=True).select_related("project", "user")
    # optional: testimonials ko bhi niche dikhado
    testimonials = Testimonial.objects.all()
    # average rating
    avg = None
    if reviews.exists():
        avg = round(sum(r.rating for r in reviews) / reviews.count(), 1)
    return render(request, 'core/reviews.html', {
        'reviews': reviews,
        'testimonials': testimonials,
        'avg': avg,
        'count': reviews.count()
    })

@login_required(login_url='/client/login/')
def review_new(request, project_id):
    project = get_object_or_404(Project, pk=project_id, client=request.user)
    if project.status != 'done':
        messages.error(request, "You can rate only after the project is delivered.")
        return redirect('/projects/')  # ya project detail

    # one review per project per user
    if Review.objects.filter(user=request.user, project=project).exists():
        messages.info(request, "You have already submitted a review for this project.")
        return redirect('/projects/')

    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        comment = (request.POST.get("comment") or "").strip()
        if rating < 1 or rating > 5:
            messages.error(request, "Please choose a rating between 1 and 5.")
        else:
            Review.objects.create(user=request.user, project=project, rating=rating, comment=comment)
            messages.success(request, "Thanks! Your review has been submitted.")
            return redirect('/reviews/')
    return render(request, 'core/review_form.html', {'project': project})

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks! Your message has been submitted. We'll contact you soon.")
            return redirect("/contact/")
        else:
            messages.error(request, "Please fix the errors and try again.")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})




def domain_check(request):
    q = request.GET.get('q','')
    # Fake availability for demo
    import random
    available = bool(random.getrandbits(1))
    return JsonResponse({'domain': q, 'available': available})
 


def dashboard(request):
    categories = PricingCategory.objects.filter(is_active=True).order_by("sort_order", "name")
    return render(request, 'core/dashboard.html', {'categories': categories})


@login_required(login_url='/client/login/')
def order(request):
    return render(request, 'core/order.html')


def about(request):
    return render(request, 'core/about.html')

