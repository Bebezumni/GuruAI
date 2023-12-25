
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class ChatUser(models.Model):
    # Your existing fields here
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    messenger = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    messenger_id = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)
    e_mail = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.user_name

class UserMessage(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class AiAnswer(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    ai_prefix = models.TextField()
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Company(models.Model):
    name = models.CharField(max_length=255)
    login = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    instruction = models.CharField(max_length=3000)
