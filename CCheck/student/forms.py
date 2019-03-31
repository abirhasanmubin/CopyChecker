from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AssignmentDone
from teacher.models import Assignment, Subject
from users.models import CUser


class AssignmentDoneForm(forms.ModelForm):

    class Meta:
        model = AssignmentDone
        fields = ['subject', 'assignment', 'content']

    # def __init__(self, *args, **kwargs):
    #     super(AssignmentDoneForm, self).__init__(*args, **kwargs)
    #     user = get_object_or_404(CUser, username=self.kwargs.get('username'))
    #     self.fields['subject'].queryset = Subject.objects.filter(
    #         teacher=user).order_by('sub_id')
    #     self.fields['assignment'].queryset = Assignment.objects.filter(
    #         teacher=user).filter(subject=form.instance.subject).order_by('-date_posted')
