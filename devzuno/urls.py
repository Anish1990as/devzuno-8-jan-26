
from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('about/', core_views.about, name='about'),
    path('pricing/', core_views.pricing, name='pricing'),
    path('portfolio/', core_views.portfolio, name='portfolio'),
    path('reviews/', core_views.reviews, name='reviews'),
    path('reviews/new/<int:project_id>/', core_views.review_new, name='review_new'),
    path('contact/', core_views.contact, name='contact'),
    path('order/', core_views.order, name='order'),
    path('domains/check/', core_views.domain_check, name='domain_check'),
    path('about/', core_views.about, name='about'),

    path('billing/', include('billing.urls')),
    path('support/', include('support.urls')),
    path('projects/', include('projects.urls')),
    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('client/', include(("accounts.urls", "accounts"), namespace="accounts")),
    path('client/', include('django.contrib.auth.urls')),
 

]


# Add this at the end:

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    