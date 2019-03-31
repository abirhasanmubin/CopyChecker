from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from pprint import pprint
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from users.models import CUser
from .models import Subject, Assignment
from .decorators import teacher_required
from student.models import AssignmentDone
from difflib import SequenceMatcher
import difflib
from . import difference as dif


class SubjectListView(ListView):
    model = Subject
    template = 'teacher/subject_list.html'
    context_object_name = 'subjects'
    ordering = ['sub_id']
    paginate_by = 5


class UserSubjectListView(ListView):
    model = Subject
    template = 'teacher/user_subjects.html'
    context_object_name = 'subjects'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(CUser, username=self.kwargs.get('username'))
        return Subject.objects.filter(teacher=user).order_by('sub_id')


class SubjectDetailView(DetailView):
    model = Subject


class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    fields = ['sub_id', 'title']

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class SubjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Subject
    fields = ['sub_id', 'title']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        subject = self.get_object()
        if self.request.user == subject.teacher:
            return True
        return False


class SubjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Subject
    success_url = 'user-subjects'

    def test_func(self):
        subject = self.get_object()
        if self.request.user == subject.teacher:
            return True
        return False


"""
"""


class AssignmentListView(ListView):
    model = Assignment
    template = 'teacher/assignment_list.html'
    context_object_name = 'assignments'
    ordering = ['-date_posted']
    paginate_by = 5


class UserAssignmentListView(ListView):
    model = Assignment
    template = 'teacher/user_assignments.html'
    context_object_name = 'assignments'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(CUser, username=self.kwargs.get('username'))
        return Assignment.objects.filter(teacher=user).order_by('-date_posted')


class AssignmentDetailView(DetailView):
    model = Assignment


class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    fields = ['subject', 'title', 'content']

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        user = get_object_or_404(CUser, username=self.kwargs.get('username'))
        return Subject.objects.filter(teacher=user).order_by('sub_id')


class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    fields = ['subject', 'title', 'content']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        assignment = self.get_object()
        if self.request.user == assignment.teacher:
            return True
        return False


class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Assignment
    success_url = 'user-assignments'

    def test_func(self):
        assignment = self.get_object()
        if self.request.user == assignment.teacher:
            return True
        return False


def result(request, **kwargs):

    assignment = Assignment.objects.get(pk=kwargs.get('pk'))
    assignments = AssignmentDone.objects.filter(
        assignment=assignment).order_by('date_uploaded')

    results = []
    for i in assignments:
        dict = {
            'assignmentdone': i,
            'match': 0.0,
            'matchwith': None
        }
        ma = 0.0
        for j in assignments:
            if i == j:
                continue
            m = SequenceMatcher(None, i.content, j.content)
            a = m.ratio() * 100
            if(ma < a):
                dict['match'] = a
                dict['matchwith'] = j
        results.append(dict)
    context = {
        'results': results
    }

    return render(request, 'teacher/assignment_result.html', context)


def result_details(request, **kwargs):

    as1 = AssignmentDone.objects.filter(pk=kwargs.get('pk1'))
    as2 = AssignmentDone.objects.filter(pk=kwargs.get('pk2'))
    m = as1[0].content.splitlines()
    n = as2[0].content.splitlines()
    diff = difflib.HtmlDiff(tabsize=4).make_table(m, n)
    context = {
        'table': diff
    }

    return render(request, 'teacher/assignment_result_details.html', context)
