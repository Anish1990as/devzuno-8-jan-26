
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts" 

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('services/', views.services, name='services'),
    path('invoices/', views.invoices, name='invoices'),
    path('quotes/', views.quotes, name='quotes'),
    path('tickets/', views.tickets, name='tickets'),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path('projects/', views.projects, name='client_projects'),
    path('domains/', views.domains, name='domains'),
    path("services/", views.services, name="services"),
    path("services/buy/<slug:plan_slug>/", views.service_buy, name="service_buy"),
    path("services/cancel/<int:pk>/", views.service_cancel, name="service_cancel"),
    path("services/resume/<int:pk>/", views.service_resume, name="service_resume"),
    path("services/change/<int:pk>/", views.service_change_plan, name="service_change_plan"),
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='accounts/forgot_password.html'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),


]
