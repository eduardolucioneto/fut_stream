from django.db import models
from django.conf import settings

class GameEvent(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('LIVE', 'Live'),
        ('ENDED', 'Ended'),
    ]

    title = models.CharField(max_length=200)
    date_time = models.DateTimeField()
    team_a = models.CharField(max_length=100)
    team_b = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} - {self.date_time.strftime('%d/%m %H:%M')}"
