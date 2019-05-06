from django.urls import path
from django.http import HttpResponse
from .views import (

    SubjectListView,
    SubjectDetailView,
    SubjectCreateView,
    SubjectUpdateView,
    SubjectDeleteView,
    UserSubjectListView,

    AssignmentListView,
    AssignmentDetailView,
    AssignmentCreateView,
    AssignmentUpdateView,
    AssignmentDeleteView,
    UserAssignmentListView

)
from . import views as te_view

urlpatterns = [
    path('subject/', SubjectListView.as_view(), name='teacher-subjects'),
    path('subject/<str:username>',
         UserSubjectListView.as_view(), name='user-subjects'),
    path('subject/<int:pk>/', SubjectDetailView.as_view(), name='subject-detail'),
    path('subject/new/', SubjectCreateView.as_view(), name='subject-create'),
    path('subject/<int:pk>/update/',
         SubjectUpdateView.as_view(), name='subject-update'),
    path('subject/<int:pk>/delete/',
         SubjectDeleteView.as_view(), name='subject-delete'),

    path('assignment/<int:subpk>/new/', AssignmentCreateView.as_view(),
         name='assignment-create'),
    path('assignment/<int:pk>/', AssignmentDetailView.as_view(),
         name='assignment-detail'),
    path('assignment/<int:pk>/update/',
         AssignmentUpdateView.as_view(), name='assignment-update'),
    path('assignment/<int:pk>/delete/',
         AssignmentDeleteView.as_view(), name='assignment-delete'),
    path('assignment/<int:pk>/result/',
         te_view.result, name='assignment-result'),
    path('assignment/<int:pk>/result/details/<int:pk1>/<int:pk2>/',
         te_view.result_details, name='assignment-result-details'),
    path('assignment/', AssignmentListView.as_view(), name='teacher-assignments'),
    path('assignment/<str:username>',
         UserAssignmentListView.as_view(), name='user-assignments'),


]
