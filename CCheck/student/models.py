from django.db import models
from users.models import CUser
from django.urls import reverse
from django.utils import timezone
from teacher.models import Subject, Assignment
# Create your models here.


class AssignmentDone(models.Model):
    content = models.TextField(default="")
    student = models.ForeignKey(CUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    date_uploaded = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('assignmentdone-detail', kwargs={'pk': self.pk})
