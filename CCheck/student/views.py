from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .decorators import student_required
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
    fields = ['content']

    def form_valid(self, form):
        form.instance.student = self.request.user
        form.instance.assignment = Assignment.objects.filter(
            pk=self.kwargs.get('as'))[0]
        form.instance.subject = form.instance.assignment.subject
        return super().form_valid(form)


class AssignmentDoneUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AssignmentDone
    fields = ['content', ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        ad = self.get_object()
        if self.request.user == ad.student:
            return True
        return False


class AssignmentDoneDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AssignmentDone

    def test_func(self):
        ad = self.get_object()
        if self.request.user == ad.student:
            return True
        return False

    def get_success_url(self):
        return reverse('teacher-subjects')
