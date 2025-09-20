from django.db import models
from django.utils import timezone

class RegistroSeguridad(models.Model):
    TIPOS = (('ronda', 'Ronda'), ('incidente', 'Incidente'), ('reporte', 'Reporte'))
    ORIGENES = (('seguridad', 'Seguridad'), ('residente', 'Residente'))
    PRIORIDADES = (('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'))
    ESTADOS = (('pendiente', 'Pendiente'), ('en_revision', 'En Revisión'), ('resuelto', 'Resuelto'))

    user = models.ForeignKey('usuarios.User', on_delete=models.CASCADE, related_name='registros_seguridad')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    origen = models.CharField(max_length=20, choices=ORIGENES)
    fecha_hora = models.DateTimeField(default=timezone.now)
    ubicacion = models.CharField(max_length=255)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    resuelto_por = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_resueltos')
    fecha_resolucion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Registro de {self.get_origen_display()}: {self.descripcion[:50]}"


class Reclamo(models.Model):
    TIPOS = (('reclamo', 'Reclamo'), ('sugerencia', 'Sugerencia'))
    ESTADOS = (('pendiente', 'Pendiente'), ('abierto', 'Abierto'), ('resuelto', 'Resuelto'))
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    adjunto = models.FileField(upload_to='reclamos/adjuntos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    respuesta = models.TextField(blank=True, null=True)
    residente = models.ForeignKey('residentes.Residente', on_delete=models.CASCADE, related_name='reclamos')
    empleado = models.ForeignKey('empleados.Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name='reclamos_asignados')

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"
