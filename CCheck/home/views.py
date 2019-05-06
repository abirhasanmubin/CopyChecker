from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)


def home(request):
    return render(request, 'home/home.html', context)


def home(request):
    # if request.user.is_authenticated:
    #     if request.user.profile.is_teacher:
    #         return render(request, 'home/home.html')
    #     else:
    #         return render(request, 'home/home.html')
    return render(request, 'home/home.html')


def about(request):
    return render(request, 'home/about.html', {'title': 'About'})
