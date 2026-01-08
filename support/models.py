# support/models.py
from django.conf import settings
from django.db import models

# Use the AUTH_USER_MODEL string directly in FK to avoid import confusion
USER_MODEL = settings.AUTH_USER_MODEL


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("pending", "Pending"),
        ("answered", "Answered"),
        ("closed", "Closed"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]
    DEPT_CHOICES = [
        ("general", "General"),
        ("billing", "Billing"),
        ("technical", "Technical"),
        ("sales", "Sales"),
    ]

    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    subject = models.CharField(max_length=200)
    # This is a convenience body field for the opening post (optional)
    message = models.TextField(default="", blank=True)
    department = models.CharField(max_length=20, choices=DEPT_CHOICES, default="general", db_index=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open", db_index=True)
    attachment = models.FileField(upload_to="tickets/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-created_at")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["department"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"#{self.id} - {self.subject}"


def ticket_attachment_path(instance, filename):
    # media/tickets/<ticket_id>/<filename>
    return f"tickets/{instance.ticket_id}/{filename}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    # NOTE: field is named 'author' (not 'user'), so admin must use 'author'
    author = models.ForeignKey(USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_messages")
    is_staff_reply = models.BooleanField(default=False)
    message = models.TextField()
    attachment = models.FileField(upload_to=ticket_attachment_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        who = "Staff" if self.is_staff_reply else "Client"
        return f"{who} message on #{self.ticket_id}"

    def short_text(self) -> str:
        txt = (self.message or "").strip()
        return (txt[:80] + "…") if len(txt) > 80 else txt
