from django import forms
from models import Question


Q_PLACEHOLDER = 'Ask your question in 140 characters'

class QuestionForm(forms.ModelForm):
    """Question Form."""
    class Meta:
        model = Question
        fields = ['question']
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': Q_PLACEHOLDER})
            }
