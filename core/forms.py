from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """The Contact page form, built from the ContactMessage model.
    The model sets the maximum lengths and checks the email; this form adds minimum lengths."""

    MIN_LENGTHS = {"name": 2, "subject": 3, "message": 10}

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap class for every field, set once here instead of in the template
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["name"].widget.attrs["autocomplete"] = "name"
        self.fields["email"].widget.attrs["autocomplete"] = "email"

    def clean(self):
        """Checks the minimum lengths, then marks every field with an error in red."""
        cleaned = super().clean()
        for field_name, minimum in self.MIN_LENGTHS.items():
            value = cleaned.get(field_name)
            if value and len(value) < minimum:
                self.add_error(field_name, f"Enter at least {minimum} characters.")

        # Bootstrap shows a red border on inputs with the is-invalid class
        for field_name in self.errors:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs["class"] += " is-invalid"
        return cleaned