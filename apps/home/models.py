
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ChatUser(models.Model):
    # Your existing fields here
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    messenger = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user_name



class UserMessage(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class AiAnswer(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    message_text = models.TextField()
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
