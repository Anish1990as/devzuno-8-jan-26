from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
]
