from django.db import models
from django.utils import timezone

class Comunicado(models.Model):
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    tipo = models.CharField(max_length=50)
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey('usuarios.User', on_delete=models.CASCADE, related_name='comunicados')
    notificado = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
