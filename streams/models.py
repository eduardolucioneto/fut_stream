from django.db import models
from django.conf import settings
from schedule.models import GameEvent

class StreamRoom(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streams')
    game = models.ForeignKey(GameEvent, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    is_live = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='watching', blank=True)

    def __str__(self):
        return f"{self.title} by {self.host.username}"
