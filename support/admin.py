# support/admin.py
from django.contrib import admin
from .models import Ticket, TicketMessage


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    fields = ("created_at", "author", "is_staff_reply", "short_msg", "attachment")
    readonly_fields = ("created_at", "short_msg")
    show_change_link = True

    def short_msg(self, obj):
        return obj.short_text()
    short_msg.short_description = "Message"


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "user", "department", "priority", "status", "created_at", "updated_at")
    list_filter = ("status", "priority", "department", "created_at")
    search_fields = ("subject", "message", "user__username", "user__email")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [TicketMessageInline]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    # IMPORTANT: use 'author' (your model field), not 'user'
    list_display = ("id", "ticket", "author", "is_staff_reply", "created_at", "short_msg")
    list_filter = ("is_staff_reply", "created_at")
    search_fields = ("message", "ticket__subject", "author__username", "author__email")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("ticket",)

    def short_msg(self, obj):
        return obj.short_text()
    short_msg.short_description = "Message"
