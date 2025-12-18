from django.db import models
from cloudinary.models import CloudinaryField
from usuarios.models import User
from residentes.models import Residente
from empleados.models import Empleado

class RegistroAcceso(models.Model):
    TIPO_PERSONA_CHOICES = [
        ('Residente', 'Residente'),
        ('Visitante', 'Visitante'),
        ('Empleado', 'Empleado'),
        ('Proveedor', 'Proveedor'),
        ('Otro', 'Otro'),
    ]
    TIPO_ACCESO_CHOICES = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
    ]

    tipo_persona = models.CharField(max_length=50, choices=TIPO_PERSONA_CHOICES)
    nombre_completo = models.CharField(max_length=255)
    ci = models.CharField(max_length=20, blank=True, null=True, verbose_name="Cédula de Identidad")
    motivo = models.TextField(blank=True, null=True)
    tipo_acceso = models.CharField(max_length=10, choices=TIPO_ACCESO_CHOICES)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    # Cloudinary field for the photo
    foto = CloudinaryField('foto', null=True, blank=True)

    # Link to existing Residente or Empleado
    residente = models.ForeignKey(Residente, on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_acceso')
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_acceso')

    # Link to the user who created the record
    registrado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='registros_de_acceso'
    )

    def __str__(self):
        detail = self.ci if self.ci else (self.residente.nombre_completo if self.residente else (self.empleado.nombre_completo if self.empleado else self.nombre_completo))
        return f"{self.tipo_acceso} de {detail} ({self.tipo_persona}) - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Registro de Acceso"
        verbose_name_plural = "Registros de Accesos"
        ordering = ['-fecha_hora']