from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # yahi sabse important hai:
    search_fields = ("name", "client__username", "client__email")
    list_display = ("name", "client", "status")
    list_filter = ("status",)