from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator

from models import Question


QUESTION = 'Ask your question in 140 characters'
ANSWER = 'Reply to question in 140 characters'


class QuestionForm(forms.ModelForm):
    """Question Form."""
    question = forms.CharField(
        validators=[MaxLengthValidator(140), MinLengthValidator(10)],
        max_length=140, widget=forms.TextInput(attrs={'placeholder': QUESTION,
                                                      'class': 'form-control',
                                                      'required': 'required'}))
    answer = forms.CharField(
        validators=[MaxLengthValidator(140)],
        required=False,
        max_length=140, widget=forms.TextInput(attrs={'placeholder': ANSWER,
                                                      'class': 'form-control'}))

    class Meta:
        model = Question
        fields = ['question', 'answer']

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['question'].required = False

    def clean(self):
        super(QuestionForm, self).clean()
        cdata = self.cleaned_data
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
