from django.db import models
from users.models import CUser
from django.urls import reverse
from django.utils import timezone
# Create your models here.


class Subject(models.Model):
    sub_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    teacher = models.ForeignKey(CUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.sub_id

    def get_absolute_url(self):
        return reverse('subject-detail', kwargs={'pk': self.pk})


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(default="")
    teacher = models.ForeignKey(CUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('assignment-detail', kwargs={'pk': self.pk})
