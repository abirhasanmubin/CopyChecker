from django import forms
from .models import CUser, Subject, Assignment
from .fields import GroupedModelChoiceField


class AssignmentCreationForm(forms.ModelForm):

    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.filter(
            teacher=self.request.user)
