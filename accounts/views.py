# accounts/views.py
from datetime import timedelta

from django.apps import apps
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import password_validation
from django.utils import timezone

from .forms import RegisterForm

User = get_user_model()


# ----- Helpers -----
def _get_profile_model():
    try:
        return apps.get_model("core", "Profile")
    except Exception:
        return None


def _get_or_create_profile(user):
    Profile = _get_profile_model()
    if not Profile:
        return None
    obj, _ = Profile.objects.get_or_create(user=user, defaults={"country_code": "+91"})
    return obj


# ------------------------------
# Registration
# ------------------------------
def register(request):
    """
    Create a user (via RegisterForm), optionally create a core.Profile and redirect to login.
    """
    Profile = _get_profile_model()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email", "") or ""
            user.save()

            # create or update profile if model exists
            try:
                if Profile:
                    prof, _ = Profile.objects.get_or_create(user=user)
                    prof.country_code = form.cleaned_data.get("country_code", "+91") or "+91"
                    prof.phone = form.cleaned_data.get("phone", "") or ""
                    prof.save()
            except Exception:
                # fail gracefully if profile shape is different
                pass

            messages.success(request, "Account created successfully. Please login.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


# ------------------------------
# Profile (tabbed)
# ------------------------------
@login_required
def profile(request):
    """
    Handles three tabs via 'form_kind' POST param: account, profile (contact), security.
    """
    prof = _get_or_create_profile(request.user)

    if request.method == "POST":
        kind = (request.POST.get("form_kind") or "").strip()

        # ----- ACCOUNT TAB -----
        if kind == "account":
            request.user.first_name = (request.POST.get("first_name") or "").strip()
            request.user.last_name = (request.POST.get("last_name") or "").strip()
            request.user.email = (request.POST.get("email") or "").strip()
            request.user.save()

            if prof and request.FILES.get("avatar"):
                prof.avatar = request.FILES["avatar"]
                prof.save()

            messages.success(request, "Account updated.")
            return redirect(reverse("accounts:profile") + "?saved=1&edit=account")

        # ----- CONTACT & ADDRESS TAB -----
        elif kind == "profile":
            if not prof:
                messages.error(request, "Profile model not available.")
                return redirect(reverse("accounts:profile"))

            cc_post = (request.POST.get("country_code") or "").strip()
            if cc_post:
                prof.country_code = cc_post

            prof.phone = (request.POST.get("phone") or "").strip()
            prof.whatsapp = (request.POST.get("whatsapp") or "").strip()
            prof.address = (request.POST.get("address") or "").strip()
            prof.city = (request.POST.get("city") or "").strip()
            prof.state = (request.POST.get("state") or "").strip()
            prof.country = (request.POST.get("country") or "").strip()
            prof.pincode = (request.POST.get("pincode") or "").strip()
            prof.company = (request.POST.get("company") or "").strip()
            prof.tax_id = (request.POST.get("tax_id") or "").strip()
            prof.save()

            messages.success(request, "Contact & address updated.")
            return redirect(reverse("accounts:profile") + "?saved=1&edit=contact")

        # ----- SECURITY TAB -----
        elif kind == "security":
            old = request.POST.get("old_password") or ""
            new1 = request.POST.get("new_password1") or ""
            new2 = request.POST.get("new_password2") or ""

            if not request.user.check_password(old):
                messages.error(request, "Current password is incorrect.")
                return redirect(reverse("accounts:profile") + "?edit=security")

            if new1 != new2:
                messages.error(request, "New passwords do not match.")
                return redirect(reverse("accounts:profile") + "?edit=security")

            try:
                password_validation.validate_password(new1, request.user)
            except Exception as e:
                messages.error(request, "; ".join(getattr(e, "messages", [str(e)])))
                return redirect(reverse("accounts:profile") + "?edit=security")

            request.user.set_password(new1)
            request.user.save()
            update_session_auth_hash(request, request.user)

            messages.success(request, "Password updated successfully.")
            return redirect(reverse("accounts:profile") + "?saved=1&edit=security")

        else:
            messages.error(request, "Invalid action.")
            return redirect(reverse("accounts:profile"))

    return render(request, "accounts/profile.html", {"profile": prof})


# ------------------------------
# Services / subscriptions
# ------------------------------
@login_required
def services(request):
    ServiceSubscription = apps.get_model("billing", "ServiceSubscription")
    ServiceCategory = apps.get_model("billing", "ServiceCategory")

    subs = (
        ServiceSubscription.objects.select_related("plan", "plan__category")
        .filter(user=request.user)
        .order_by("-created_at")
    )

    categories = ServiceCategory.objects.prefetch_related("plans").all()
    return render(request, "accounts/services.html", {"subs": subs, "categories": categories})


@login_required
def service_buy(request, plan_slug):
    ServicePlan = apps.get_model("billing", "ServicePlan")
    ServiceSubscription = apps.get_model("billing", "ServiceSubscription")

    plan = get_object_or_404(ServicePlan, slug=plan_slug, is_active=True)
    period = request.GET.get("period", "monthly")
    if period not in ("monthly", "yearly"):
        period = "monthly"

    sub = ServiceSubscription.objects.create(
        user=request.user,
        plan=plan,
        billing_period=period,
        status="active",
        started_at=timezone.now(),
        renews_at=timezone.now() + timedelta(days=365 if period == "yearly" else 30),
    )
    messages.success(request, f"Subscribed to {plan.name} ({period}).")
    return redirect(reverse("accounts:services"))


@login_required
def service_cancel(request, pk):
    ServiceSubscription = apps.get_model("billing", "ServiceSubscription")
    sub = get_object_or_404(ServiceSubscription, pk=pk, user=request.user)

    if getattr(sub, "status", "") != "active":
        messages.warning(request, "This subscription is not active.")
        return redirect("accounts:services")

    sub.cancel_at_period_end = True
    sub.save(update_fields=["cancel_at_period_end"])
    messages.success(request, "Subscription will cancel at the end of the current period.")
    return redirect("accounts:services")


@login_required
def service_resume(request, pk):
    ServiceSubscription = apps.get_model("billing", "ServiceSubscription")
    sub = get_object_or_404(ServiceSubscription, pk=pk, user=request.user)

    if getattr(sub, "status", "") != "active":
        messages.warning(request, "This subscription is not active.")
        return redirect("accounts:services")

    sub.cancel_at_period_end = False
    sub.save(update_fields=["cancel_at_period_end"])
    messages.success(request, "Auto-renew has been resumed.")
    return redirect("accounts:services")


@login_required
def service_change_plan(request, pk):
    ServiceSubscription = apps.get_model("billing", "ServiceSubscription")
    ServicePlan = apps.get_model("billing", "ServicePlan")

    sub = get_object_or_404(ServiceSubscription, pk=pk, user=request.user)
    siblings = ServicePlan.objects.filter(category=sub.plan.category, is_active=True).order_by("price_monthly")

    if request.method == "POST":
        new_slug = request.POST.get("plan")
        new_period = request.POST.get("period") or sub.billing_period

        try:
            new_plan = siblings.get(slug=new_slug)
        except ServicePlan.DoesNotExist:
            messages.error(request, "Invalid plan.")
            return redirect("accounts:services")

        sub.plan = new_plan
        sub.billing_period = new_period if new_period in ("monthly", "yearly") else sub.billing_period
        sub.renews_at = timezone.now() + timedelta(days=365 if sub.billing_period == "yearly" else 30)
        sub.cancel_at_period_end = False
        sub.save()

        messages.success(request, f"Plan changed to {new_plan.name}.")
        return redirect("accounts:services")

    return render(request, "accounts/change_plan.html", {"sub": sub, "plans": siblings})


# ------------------------------
# Invoices / quotes
# ------------------------------
@login_required
def invoices(request):
    data = []
    try:
        Invoice = apps.get_model("billing", "Invoice")
        if hasattr(Invoice, "objects"):
            try:
                data = Invoice.objects.filter(order__user=request.user).order_by("-created_at")
            except Exception:
                data = Invoice.objects.filter(user=request.user).order_by("-created_at")
    except Exception:
        data = []
    return render(request, "accounts/invoices.html", {"invoices": data})


@login_required
def quotes(request):
    return render(request, "accounts/quotes.html")


# ------------------------------
# Tickets
# ------------------------------
@login_required
def tickets(request):
    Ticket = apps.get_model("support", "Ticket")

    # CREATE (from modal)
    if request.method == "POST" and request.POST.get("form_kind") == "create_ticket":
        subject = (request.POST.get("subject") or "").strip()
        message_txt = (request.POST.get("message") or "").strip()
        priority = (request.POST.get("priority") or "medium").lower()
        department = (request.POST.get("department") or "general").lower()
        file_obj = request.FILES.get("attachment")

        if priority not in {"low", "medium", "high"}:
            priority = "medium"
        if department not in {"general", "billing", "technical", "sales"}:
            department = "general"

        if not subject or not message_txt:
            messages.error(request, "Subject and message are required.")
            return redirect("accounts:tickets")

        Ticket.objects.create(
            user=request.user,
            subject=subject,
            message=message_txt,
            priority=priority,
            department=department,
            attachment=file_obj,
        )
        messages.success(request, "Ticket submitted. Our team will contact you soon.")
        return redirect("accounts:tickets")

    # LIST / FILTER
    qs = Ticket.objects.filter(user=request.user).order_by("-updated_at")
    status = request.GET.get("status")
    if status in {"open", "pending", "answered", "closed"}:
        qs = qs.filter(status=status)

    return render(request, "accounts/tickets.html", {"tickets": qs})


@login_required
def ticket_detail(request, pk):
    Ticket = apps.get_model("support", "Ticket")
    TicketMessage = apps.get_model("support", "TicketMessage")

    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)

    # Close via query param
    if request.method == "GET" and request.GET.get("action") == "close":
        ticket.status = "closed"
        ticket.save(update_fields=["status"])
        messages.success(request, "Ticket closed.")
        return redirect("accounts:ticket_detail", pk)

    # Add reply
    if request.method == "POST" and request.POST.get("form_kind") == "reply":
        text = (request.POST.get("message") or "").strip()
        attachment = request.FILES.get("attachment")

        if not text:
            messages.error(request, "Message cannot be empty.")
            return redirect("accounts:ticket_detail", pk)

        # Try save via instance (flexible)
        tm = TicketMessage()

        # ticket
        if hasattr(tm, "ticket"):
            tm.ticket = ticket
        elif hasattr(tm, "ticket_id"):
            tm.ticket_id = ticket.id

        # author/user
        if hasattr(tm, "author"):
            tm.author = request.user
        elif hasattr(tm, "user"):
            tm.user = request.user

        # message/body
        if hasattr(tm, "message"):
            tm.message = text
        elif hasattr(tm, "body"):
            tm.body = text

        # flags
        if hasattr(tm, "is_staff_reply"):
            tm.is_staff_reply = False
        elif hasattr(tm, "is_staff"):
            tm.is_staff = False
        elif hasattr(tm, "is_client"):
            tm.is_client = True

        if attachment and hasattr(tm, "attachment"):
            tm.attachment = attachment

        try:
            tm.save()
        except Exception:
            # fallback create
            create_kwargs = {}

            if "ticket" in [f.name for f in TicketMessage._meta.fields]:
                create_kwargs["ticket"] = ticket
            elif "ticket_id" in [f.name for f in TicketMessage._meta.fields]:
                create_kwargs["ticket_id"] = ticket.id

            if "author" in [f.name for f in TicketMessage._meta.fields]:
                create_kwargs["author"] = request.user
            elif "user" in [f.name for f in TicketMessage._meta.fields]:
                create_kwargs["user"] = request.user

            if "message" in [f.name for f in TicketMessage._meta.fields]:
                create_kwargs["message"] = text
            elif "body" in [f.name for f in TicketMessage._meta.fields]:
                create_kwargs["body"] = text

            if attachment and "attachment" in [f.name for f in TicketMessage._meta.fields]:
                create_kwargs["attachment"] = attachment

            TicketMessage.objects.create(**create_kwargs)

        # If it was answered/pending, mark as open for client reply
        if ticket.status in ("answered", "pending"):
            ticket.status = "open"
            ticket.save(update_fields=["status"])

        messages.success(request, "Reply posted.")
        return redirect("accounts:ticket_detail", pk)

    msgs = TicketMessage.objects.filter(ticket=ticket).order_by("created_at")
    return render(request, "accounts/ticket_detail.html", {"ticket": ticket, "messages_qs": msgs})


# ------------------------------
# Simple pages
# ------------------------------
@login_required
def projects(request):
    return render(request, "accounts/projects.html")


@login_required
def domains(request):
    return render(request, "accounts/domains.html")
