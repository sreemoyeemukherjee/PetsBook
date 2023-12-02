from django.db import models

# Create your models here.
class Post(models.Model):
    username = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    category = models.CharField(max_length=10, choices=[('Indoor', 'Indoor'), ('Outdoor', 'Outdoor')], default='Indoor')
    tags = models.CharField(max_length=200, blank=True, null=True)
    is_flagged = models.BooleanField(default=False)