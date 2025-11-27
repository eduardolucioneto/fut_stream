from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_premium = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    can_create_stream = models.BooleanField(default=False, verbose_name="Pode criar stream")
    can_delete_stream = models.BooleanField(default=False, verbose_name="Pode deletar stream")
    valid_until = models.DateField(null=True, blank=True, verbose_name="Válido até")

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.valid_until:
            return self.valid_until < timezone.now().date()
        return False

    def __str__(self):
        return self.username
