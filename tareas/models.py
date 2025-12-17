from django.db import models
from usuarios.models import User
from empleados.models import Empleado

class Tarea(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Progreso', 'En Progreso'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]

    PRIORIDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='Media')

    # Relationships
    empleado_asignado = models.ForeignKey(
        Empleado, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tareas_asignadas'
    )
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tareas_creadas'
    )

    def __str__(self):
        return self.titulo