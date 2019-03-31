from django.urls import path
from .views import (

    AssignmentDoneListView,
    AssignmentDoneCreateView,
    AssignmentDoneDetailView,
    AssignmentDoneDeleteView,
    AssignmentDoneUpdateView,
    UserAssignmentDoneListView

)


urlpatterns = [
    path('assignmentdone/new/', AssignmentDoneCreateView.as_view(),
         name='assignmentdone-create'),
    path('assignmentdone/<int:pk>/', AssignmentDoneDetailView.as_view(),
         name='assignmentdone-detail'),
    path('assignmentdone/<int:pk>/update/',
         AssignmentDoneUpdateView.as_view(), name='assignmentdone-update'),
    path('assignmentdone/<int:pk>/delete/',
         AssignmentDoneDeleteView.as_view(), name='assignmentdone-delete'),
    path('assignmentdone/', AssignmentDoneListView.as_view(),
         name='teacher-assignmentdones'),
    path('assignmentdone/<str:username>',
         UserAssignmentDoneListView.as_view(), name='user-assignmentdones'),


]
