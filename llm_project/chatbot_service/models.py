from django.contrib.auth.models import User
from django.db import models

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session_name} ({self.user.username})"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=[("user", "User"), ("bot", "Bot")])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"
