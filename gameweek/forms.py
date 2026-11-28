from django import forms

from core.forms import BootstrapFormMixin

from .models import Comment, Fixture


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    """A chat message: the game it's about (empty means General) and 2 to 500 characters.
    Only games of the current round can be chosen."""

    class Meta:
        model = Comment
        fields = ["fixture", "text"]
        labels = {"fixture": "Talking about", "text": "Message"}
        widgets = {"text": forms.Textarea(attrs={"rows": 1, "maxlength": 500, "placeholder": "Write a message..."})}

    def __init__(self, *args, round_number=None, **kwargs):
        super().__init__(*args, **kwargs)
        topic = self.fields["fixture"]
        topic.queryset = Fixture.objects.filter(round_number=round_number).select_related("home_team", "away_team")
        topic.empty_label = "General"
        topic.label_from_instance = lambda fixture: fixture.short_label

    def clean_text(self):
        text = self.cleaned_data["text"]
        if len(text) < 2:
            raise forms.ValidationError("Write at least 2 characters.")
        return text