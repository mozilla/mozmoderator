from dal import autocomplete
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator

from .models import Event, Question

QUESTION = "Ask your question in 280 characters"
ANSWER = "Reply to question in 280 characters"
CONTACT_INFO = "Optional: Please supply a valid email address."
REJECTION_REASON = (
    "Reply to the submitter on why this question was moderated in 512 characters."
)


class QuestionForm(forms.ModelForm):
    """Question Form."""

    question = forms.CharField(
        validators=[MaxLengthValidator(280), MinLengthValidator(10)],
        max_length=280,
        widget=forms.TextInput(
            attrs={
                "placeholder": QUESTION,
                "class": "form-control",
                "required": "required",
            }
        ),
    )
    answer = forms.CharField(
        validators=[MaxLengthValidator(280)],
        required=False,
        max_length=280,
        widget=forms.TextInput(attrs={"placeholder": ANSWER, "class": "form-control"}),
    )
    submitter_contact_info = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": CONTACT_INFO, "class": "form-control"}
        ),
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"placeholder": REJECTION_REASON, "class": "form-control"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.is_locked = kwargs.pop("is_locked", False)
        super(QuestionForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields["question"].required = False

    def clean(self):
        cdata = super(QuestionForm, self).clean()
        if self.is_locked and (
            cdata.get("is_approved") or cdata.get("rejection_reason")
        ):
            raise ValidationError(
                "The question can only be moderated by event moderators"
            )

        if self.instance.id:
            cdata["question"] = self.instance.question
            # Raise an error if there is no answer
            if not cdata["answer"] and self.is_locked:
                msg = "Please provide a reply."
                self._errors["answer"] = self.error_class([msg])
            return cdata
        # Force an empty answer when saving a new form
        cdata["answer"] = ""
        return cdata

    class Meta:
        model = Question
        fields = [
            "question",
            "answer",
            "is_anonymous",
            "submitter_contact_info",
            "rejection_reason",
        ]
        widgets = {"is_anonymous": forms.CheckboxInput()}


class EventForm(forms.ModelForm):
    """Question Form."""

    moderators = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url="users-autocomplete"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(EventForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields["name"].required = True
        else:
            self.fields["moderators"].initial = User.objects.filter(id=self.user.pk)

    def clean(self):
        """
        Clean method to check post data for nda events,
        and moderated events with no moderators.
        """
        cdata = super(EventForm, self).clean()
        # Do not allow non-nda members to submit NDA events.
        if not self.user.userprofile.is_nda_member and cdata["is_nda"]:
            msg = "Only members of the NDA group can create NDA events."
            raise forms.ValidationError(msg)
        if cdata["is_moderated"] and not cdata["moderators"]:
            msg = "A moderated event requires moderators."
            raise forms.ValidationError(msg)

        return cdata

    class Meta:
        model = Event
        fields = ["name", "is_nda", "body", "is_moderated", "moderators"]
        widgets = (
            {
                "is_nda": forms.CheckboxInput(),
                "is_moderated": forms.CheckboxInput(),
            },
        )
        labels = {
            "name": "Event title",
        }
