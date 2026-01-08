# billing/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify



User = get_user_model()
User = settings.AUTH_USER_MODEL

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return f"Order #{self.pk} • {self.package} • {self.user}"
    

class Invoice(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('unpaid','Unpaid'),('paid','Paid')], default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.pk} • {self.order.package} • ₹{self.amount} • {self.status}"

class ServiceCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=32, blank=True, help_text="Emoji or icon code")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self): return self.name


BILLING_PERIODS = (
    ("monthly", "Monthly"),
    ("yearly", "Yearly"),
)

class ServicePlan(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    tagline = models.CharField(max_length=180, blank=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    features = models.TextField(blank=True, help_text="One feature per line")
    is_active = models.BooleanField(default=True)
    sort = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort", "price_monthly"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.category.slug}-{slugify(self.name)}"
            self.slug = base
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.category.name} – {self.name}"


SUBS_STATUS = (
    ("active", "Active"),
    ("pending", "Pending"),
    ("canceled", "Canceled"),
    ("expired", "Expired"),
)

class ServiceSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(ServicePlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=16, choices=SUBS_STATUS, default="active")
    billing_period = models.CharField(max_length=10, choices=BILLING_PERIODS, default="monthly")
    started_at = models.DateTimeField(default=timezone.now)
    renews_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def price(self):
        return self.plan.price_yearly if self.billing_period == "yearly" else self.plan.price_monthly

    def is_active(self):
        return self.status == "active" and not self.cancel_at_period_end
    is_active.boolean = True

    def __str__(self):
        return f"{self.user} → {self.plan} ({self.billing_period})"