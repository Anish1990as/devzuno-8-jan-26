
from django.db import models
from django.conf import settings
from django.db import models
from projects.models import Project
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from django.db import models


class HomeService(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to="home/services/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Home Our Service"
        verbose_name_plural = "Home Our Services"

    def __str__(self):
        return self.title


class WhyDevzuno(models.Model):
    point = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to="home/why/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Why Devzuno Point"
        verbose_name_plural = "Why Devzuno"

    def __str__(self):
        return self.point


class HowWeWork(models.Model):
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to="home/how/",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["step_number"]
        verbose_name = "How We Work Step"
        verbose_name_plural = "How We Work"

    def __str__(self):
        return f"{self.step_number}. {self.title}"


class HomePortfolio(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to="home/portfolio/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Our Work Item"
        verbose_name_plural = "Our Work"

    def __str__(self):
        return self.title



class PricingCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True, help_text="Emoji ya small text e.g. 📝, 🏢, 📱, 🧩")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

class PricingPlan(models.Model):
    name = models.CharField(max_length=50)
    price_text = models.CharField(max_length=50)
    features = models.TextField(help_text='One per line')
    highlight = models.BooleanField(default=False)

    category = models.ForeignKey(
        PricingCategory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="plans"
    )

    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    def save(self, *args, **kwargs):
        # 🔥 CORE LOGIC: only ONE popular plan per category
        if self.highlight and self.category:
            PricingPlan.objects.filter(
                category=self.category,
                highlight=True
            ).exclude(pk=self.pk).update(highlight=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PortfolioItem(models.Model):
    title = models.CharField(max_length=120)

    # NEW: file upload (stores under /media/portfolio/)
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)

    # Old (optional fallback; remove later if not needed)
    image_url = models.URLField(blank=True, null=True)

    project_link = models.URLField(blank=True, null=True, help_text="Optional: link to live site or demo")

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    author = models.CharField(max_length=120)
    quote = models.TextField()
    def __str__(self): return f"{self.author}"


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)  # moderation chahiye to default False kar do
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review {self.rating}/5 by {self.user} on {self.project}"

    @property
    def stars(self):
        return "★" * self.rating + "☆" * (5 - self.rating)
    

  

class ContactMessage(models.Model):
    WEBSITE_TYPES = [
        ("blog", "Blog Website"),
        ("business", "Business/Company"),
        ("ecommerce", "E-commerce"),
        ("portfolio", "Portfolio/Personal"),
        ("lms", "LMS / Course"),
        ("news", "News / Magazine"),
        ("custom", "Custom Requirement"),
    ]

    SUPPORT_LANG = [
        ("hi", "Hindi"),
        ("en", "English"),
        ("bn", "Bengali"),
        ("ta", "Tamil"),
        ("kn", "Kannada"),
        ("ml", "Malayalam"),
      ]

    name = models.CharField(max_length=120)
    email = models.EmailField()

    # Country code selector + local number; full_phone auto-computed
    country_code = models.CharField(
        max_length=6,
        help_text=_("E.164 country code like +91, +1, +44"),
        default="+91",
        blank=True,
    )
    phone = models.CharField(
        max_length=30,
        help_text=_("Local number (without country code)"),
        default="",
        blank=True,
    )
    full_phone = models.CharField(
        max_length=40,
        editable=False,
        blank=True,
        default="",
    )

    location = models.CharField(max_length=160, blank=True)
    pincode = models.CharField(max_length=12, blank=True, default="")

    website_type = models.CharField(max_length=20, choices=WEBSITE_TYPES)

    # Multi-select world languages (store codes list)
    languages = models.JSONField(default=list, blank=True)

    # Optional single support language (backward compat)
    support_language = models.CharField(max_length=20, choices=SUPPORT_LANG, blank=True)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.website_type} ({self.created_at:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        """Build full_phone like '+91 5941954999' automatically"""
        cc = (self.country_code or "").strip()
        num = (self.phone or "").strip().replace(" ", "")
        if cc and not cc.startswith("+"):
            cc = "+" + cc
        self.full_phone = f"{cc} {num}".strip()
        super().save(*args, **kwargs)




class Profile(models.Model):
    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    country_code = models.CharField(max_length=6, blank=True)
    phone        = models.CharField(max_length=30, blank=True)
    whatsapp     = models.CharField(max_length=30, blank=True)
    address      = models.CharField(max_length=255, blank=True)
    city         = models.CharField(max_length=100, blank=True)
    state        = models.CharField(max_length=100, blank=True)
    country      = models.CharField(max_length=100, blank=True)
    pincode      = models.CharField(max_length=12, blank=True)
    company      = models.CharField(max_length=160, blank=True)
    tax_id       = models.CharField(max_length=50, blank=True)
    avatar       = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} profile"
    
 
 