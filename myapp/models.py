from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class Post(models.Model):
    username = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    category = models.CharField(max_length=10, choices=[('Indoor', 'Indoor'), ('Outdoor', 'Outdoor')], default='Indoor')
    tags = models.CharField(max_length=200, blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorited_posts', blank=True)
    like_count = models.IntegerField(default=0)  # New field for like count

    def update_like_count(self):
        self.like_count = self.likes.count()
        # self.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_logged_time = models.DateTimeField(null=True, blank=True)
    has_clicked_messages = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()