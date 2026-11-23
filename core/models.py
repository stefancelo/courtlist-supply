from django.db import models


class ContactMessage(models.Model):
    """A message sent through the Contact page. Admins read them in the admin."""

    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.name})"