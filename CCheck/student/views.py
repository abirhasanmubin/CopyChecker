from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)
from users.models import CUser
from teacher.models import Subject, Assignment
from .models import AssignmentDone
from .forms import AssignmentDoneForm

# Create your views here.


class AssignmentDoneListView(ListView):
    model = AssignmentDone
    template = 'student/assignmentdone_list.html'
    context_object_name = 'assignmentdones'
    ordering = ['-date_uploaded']
    paginate_by = 5

    def get_queryset(self):
        # user = get_object_or_404(CUser, username=self.kwargs.get('username'))
        return AssignmentDone.objects.filter(student=self.request.user).order_by('-date_uploaded')


class UserAssignmentDoneListView(ListView):

    model = AssignmentDone
    template = 'student/user_assignmentdones.html'
    context_object_name = 'assignmentdones'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(CUser, username=self.kwargs.get('username'))
        return AssignmentDone.objects.filter(student=user).order_by('-date_uploaded')


class AssignmentDoneDetailView(DetailView):
    model = AssignmentDone


class AssignmentDoneCreateView(LoginRequiredMixin, CreateView):
    model = AssignmentDone
    fields = ['subject', 'assignment', 'content']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # user = get_object_or_404(CUser, username=self.kwargs.get('username'))
    #     self.fields['subject'].queryset = Subject.objects.filter(
    #         teacher=user).order_by('sub_id')
    #     self.fields['assignment'].queryset = Assignment.objects.filter(
    #         teacher=user).filter(subject=form.instance.subject).order_by('-date_posted')

    def form_valid(self, form):
        form.instance.student = self.request.user
        return super().form_valid(form)


class AssignmentDoneUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AssignmentDone
    fields = ['subject', 'assignment', 'content']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        subject = self.get_object()
        if self.request.user == subject.teacher:
            return True
        return False


class AssignmentDoneDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Subject
    success_url = 'user-assignmentdones'

    def test_func(self):
        subject = self.get_object()
        if self.request.user == subject.teacher:
            return True
        return False
