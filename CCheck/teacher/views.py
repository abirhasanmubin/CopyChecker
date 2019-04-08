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
from . import diffMatch as dm


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

    def get_context_data(self, **kwargs):
        context = super(SubjectDetailView, self).get_context_data(**kwargs)
        sub = Subject.objects.filter(pk=self.kwargs.get('pk'))[0]
        context['assignment_list'] = Assignment.objects.filter(
            subject=sub).order_by('-date_posted')
        return context


@method_decorator([login_required, teacher_required], name='dispatch')
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

    def get_context_data(self, **kwargs):
        context = super(AssignmentDetailView, self).get_context_data(**kwargs)
        asi = Assignment.objects.filter(pk=self.kwargs.get('pk'))[0]
        context['assignmentdone_list'] = AssignmentDone.objects.filter(
            assignment=asi).order_by('date_uploaded')
        return context


@method_decorator([login_required, teacher_required], name='dispatch')
class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        form.instance.subject = Subject.objects.filter(
            pk=self.kwargs.get('subpk')).first()
        pprint(form.instance.subject)
        return super().form_valid(form)

    def get_queryset(self):
        user = get_object_or_404(CUser, username=self.kwargs.get('username'))
        return Subject.objects.filter(teacher=user).order_by('sub_id')


class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    fields = ['title', 'content']

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


@login_required
@teacher_required
def result(request, **kwargs):

    asi = Assignment.objects.get(pk=kwargs.get('pk'))
    assignments = AssignmentDone.objects.filter(
        assignment=asi).order_by('date_uploaded')

    result = []

    for i in assignments:
        dict = {
            'assignmentdone': i,
            'match': 0.0,
            'matchwith': None
        }
        result.append(dict)

    for i in range(len(result)):

        ma = result[i]['match']

        for j in range(i + 1, len(result)):

            m = SequenceMatcher(
                None, result[i]['assignmentdone'].content, result[j]['assignmentdone'].content)
            a = m.ratio() * 100
            a = round(a, 2)

            if ma < a:
                ma = a
                result[i]['match'] = a
                result[j]['match'] = a
                result[i]['matchwith'] = result[j]['assignmentdone']
                result[j]['matchwith'] = result[i]['assignmentdone']

    context = {
        'results': result
    }

    return render(request, 'teacher/assignment_result.html', context)


@login_required
@teacher_required
def result_details(request, **kwargs):

    as1 = AssignmentDone.objects.filter(pk=kwargs.get('pk1'))
    as2 = AssignmentDone.objects.filter(pk=kwargs.get('pk2'))
    m = as1[0].content
    n = as2[0].content

    di = dm.diff_match()

    diff = di.diff_main(m, n)

    diff = di.diff_prettyHtml(diff)

    context = {
        'table': diff
    }

    return render(request, 'teacher/assignment_result_details.html', context)
