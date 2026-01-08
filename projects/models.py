
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Project(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=[('new','New'),('in_progress','In Progress'),('review','Review'),('done','Done')], default='new')
    def __str__(self): return self.name
