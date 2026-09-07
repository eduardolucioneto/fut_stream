from django.db import models
from django.conf import settings
from schedule.models import GameEvent
from django.utils import timezone
import uuid

class StreamRoom(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streams')
    game = models.ForeignKey(GameEvent, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    is_live = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='watching', blank=True)

    def __str__(self):
        return f"{self.title} by {self.host.username}"


class StreamParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stream = models.ForeignKey(StreamRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=6, choices=[('host', 'Host'), ('viewer', 'Viewer')])
    ready = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now)


class StreamSignal(models.Model):
    message_id = models.UUIDField(unique=True)
    source = models.ForeignKey(StreamParticipant, on_delete=models.CASCADE, related_name='sent_signals')
    target = models.ForeignKey(StreamParticipant, on_delete=models.CASCADE, related_name='received_signals')
    connection_id = models.UUIDField()
    payload = models.JSONField()
    delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['target', 'id'], name='stream_signal_target_id')]
