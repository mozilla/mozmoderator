from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator

from .models import Event, Question


class TomSelectMultiple(forms.SelectMultiple):
    """SelectMultiple enhanced with Tom Select on the client.

    Renders only currently-selected options as <option> elements; the
    rest are loaded on demand from `autocomplete_url` via fetch.
    """

    def __init__(self, autocomplete_url, attrs=None):
        merged = {
            "data-autocomplete-url": autocomplete_url,
            "class": ((attrs or {}).get("class", "") + " tom-select form-control").strip(),
        }
        merged.update({k: v for k, v in (attrs or {}).items() if k not in merged})
        super().__init__(attrs=merged)

    def optgroups(self, name, value, attrs=None):
        groups = super().optgroups(name, value, attrs)
        return [
            (group_name, [opt for opt in options if opt["selected"]], idx)
            for group_name, options, idx in groups
        ]


QUESTION = "Ask your question in 500 characters"
ANSWER = "Reply to question in 2500 characters"
CONTACT_INFO = "Optional: Please supply a valid email address."
REJECTION_REASON = "Reply to the submitter on why this question was moderated."


class QuestionForm(forms.ModelForm):
    """Question Form."""

    question = forms.CharField(
        validators=[MaxLengthValidator(500), MinLengthValidator(10)],
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "placeholder": QUESTION,
                "class": "form-control textarea-md",
                "required": "required",
                "rows": 4,
            }
        ),
    )
    answer = forms.CharField(
        required=False,
        max_length=2500,
        widget=forms.Textarea(
            attrs={
                "placeholder": ANSWER,
                "class": "form-control textarea-md",
            }
        ),
    )
    submitter_contact_info = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"placeholder": CONTACT_INFO, "class": "form-control"}
        ),
    )
    rejection_reason = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "placeholder": REJECTION_REASON,
                "class": "form-control textarea-md",
            }
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
            if "answer" in cdata and not cdata["answer"] and self.is_locked:
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
        widgets = {
            "is_anonymous": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EventForm(forms.ModelForm):
    """Question Form."""

    moderators = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=TomSelectMultiple(autocomplete_url="/u/user-autocomplete/"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(EventForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields["name"].required = True
        else:
            self.fields["moderators"].initial = User.objects.filter(id=self.user.pk)
            del self.fields["archived"]

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
        # Don't allow non-superusers to modify moderation status or moderators
        if not cdata["moderators"]:
            msg = "An event should have at least one moderator."
            raise forms.ValidationError(msg)

        return cdata

    class Meta:
        model = Event
        fields = [
            "name",
            "is_nda",
            "body",
            "is_moderated",
            "moderators",
            "archived",
            "users_can_vote",
            "event_date",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Event title"}
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control textarea-md",
                    "placeholder": "Helpful links, additional information",
                    "maxlength": "2500",
                }
            ),
            "event_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "placeholder": "Event date",
                }
            ),
            "is_nda": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_moderated": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "users_can_vote": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "archived": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Event title",
        }
