from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator

from models import Event, Question


QUESTION = 'Ask your question in 280 characters'
ANSWER = 'Reply to question in 280 characters'


class QuestionForm(forms.ModelForm):
    """Question Form."""
    question = forms.CharField(
        validators=[MaxLengthValidator(280), MinLengthValidator(10)],
        max_length=280, widget=forms.TextInput(attrs={'placeholder': QUESTION,
                                                      'class': 'form-control',
                                                      'required': 'required'}))
    answer = forms.CharField(
        validators=[MaxLengthValidator(280)],
        required=False,
        max_length=280, widget=forms.TextInput(attrs={'placeholder': ANSWER,
                                                      'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['question'].required = False

    def clean(self):
        cdata = super(QuestionForm, self).clean()

        if self.instance.id:
            cdata['question'] = self.instance.question
            # Raise an error if there is no answer
            if not cdata['answer']:
                msg = 'Please provide a reply.'
                self._errors['answer'] = self.error_class([msg])
            return cdata
        # Force an empty answer when saving a new form
        cdata['answer'] = ''
        return cdata

    class Meta:
        model = Question
        fields = ['question', 'answer', 'is_anonymous']
        widgets = {
            'is_anonymous': forms.CheckboxInput()
        }


class EventForm(forms.ModelForm):
    """Question Form."""

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['name'].required = True

    class Meta:
        model = Event
        fields = ['name', 'is_nda']
        widgets = {
            'is_nda': forms.CheckboxInput(),
        },
        labels = {
            'name': 'What\'s the name of the event?'
        }
