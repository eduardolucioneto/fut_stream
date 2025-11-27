from django.db import models
from django.conf import settings
from django.utils import timezone

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        if self.recipient:
            return f'{self.user.username} -> {self.recipient.username}: {self.content[:20]}'
        return f'{self.user.username}: {self.content[:20]}'

class UserActivity(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_activity')
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} seen at {self.last_seen}'
