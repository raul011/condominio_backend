from django.db import models
#from django.contrib.auth.models import User
from django.utils import timezone


from django.db import models
from django.contrib.auth.models import User
#aa
class DeviceToken(models.Model):
    user = models.ForeignKey('usuarios.User', on_delete=models.CASCADE, related_name='device_tokens') 
    token = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}..."



