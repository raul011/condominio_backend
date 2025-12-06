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


class ComunicadoResidente(models.Model):
    ESTADOS = (('enviado', 'Enviado'), ('leído', 'Leído'))
    comunicado = models.ForeignKey(Comunicado, on_delete=models.CASCADE, related_name='destinatarios')
    residente = models.ForeignKey('residentes.Residente', on_delete=models.CASCADE, related_name='comunicados_recibidos')
    fecha_envio = models.DateTimeField(default=timezone.now)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='enviado')

    def __str__(self):
        return f"{self.comunicado.titulo} - {self.residente.nombre_completo}"
