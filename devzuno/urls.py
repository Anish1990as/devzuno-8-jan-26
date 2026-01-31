
from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap


def robots_txt(request):               # 👈 IMPORTANT
    return HttpResponse(
        "User-agent: *\nAllow: /\n\nSitemap: https://www.devzuno.com/sitemap.xml",
        content_type="text/plain"
    )

sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('anishshesh/', admin.site.urls),
    path('', core_views.home, name='home'),
  #  path("", include("accounts.urls")),
    path('pricing/', core_views.pricing, name='pricing'),
    path('portfolio/', core_views.portfolio, name='portfolio'),
    path('reviews/', core_views.reviews, name='reviews'),
    path('reviews/new/<int:project_id>/', core_views.review_new, name='review_new'),
    path('contact/', core_views.contact, name='contact'),
    path('order/', core_views.order, name='order'),
    path('about/', core_views.about, name='about'),
    path("privacy_policy/", core_views.privacy_policy, name="privacy_policy"),

    path('billing/', include('billing.urls')),
    path('support/', include('support.urls')),
    path('projects/', include('projects.urls')),
    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('client/', include(("accounts.urls", "accounts"), namespace="accounts")),
    path('client/', include('django.contrib.auth.urls')),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}),
    path("services/", core_views.services, name="services"),


]

# Add this at the end:

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    