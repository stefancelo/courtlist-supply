from django import forms

from .models import ContactMessage


class BootstrapFormMixin:
    """Gives every field Bootstrap's styling: form-select for dropdowns, form-control for
    everything else, and is-invalid (a red border) on fields that failed validation.
    Every form on the site includes it, so the styling is written once."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                css = "form-select"
            else:
                css = "form-control"
            field.widget.attrs["class"] = css

    def full_clean(self):
        """Runs Django's normal validation, then marks every field with an error in red."""
        super().full_clean()
        for field_name in self.errors:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs["class"] += " is-invalid"


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    """The Contact page form, built from the ContactMessage model.
    The model sets the maximum lengths and checks the email; this form adds minimum lengths."""

    MIN_LENGTHS = {"name": 2, "subject": 3, "message": 10}

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["autocomplete"] = "name"
        self.fields["email"].widget.attrs["autocomplete"] = "email"

    def clean(self):
        """Checks the minimum lengths on top of the model's own rules."""
        cleaned = super().clean()
        for field_name, minimum in self.MIN_LENGTHS.items():
            value = cleaned.get(field_name)
            if value and len(value) < minimum:
                self.add_error(field_name, f"Enter at least {minimum} characters.")
        return cleaned