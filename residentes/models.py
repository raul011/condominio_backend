from django.db import models
from django.utils import timezone

class Residente(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    ci = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    tipo_residente = models.CharField(max_length=50, help_text="Ej: Propietario, Inquilino")

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return self.nombre_completo


class Unidad(models.Model):
    codigo = models.CharField(max_length=50, unique=True, help_text="Ej: 'A-101'")
    placa = models.CharField(max_length=20, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    capacidad = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, default='activa')
    personas_por_unidad = models.PositiveIntegerField(default=1)
    tiene_mascotas = models.BooleanField(default=False)
    vehiculos = models.PositiveIntegerField(default=0)
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='unidades')

    def __str__(self):
        return f"Unidad {self.codigo}"


class Visita(models.Model):
    ESTADOS = (('pendiente', 'Pendiente'), ('en_curso', 'En Curso'), ('finalizada', 'Finalizada'))
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='visitas')
    nombre_visitante = models.CharField(max_length=255)
    ci_visitante = models.CharField(max_length=20)
    placa_vehiculo = models.CharField(max_length=15, blank=True, null=True)
    motivo = models.CharField(max_length=255)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    codigo = models.CharField(max_length=10, unique=True, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    hora_entrada = models.DateTimeField(blank=True, null=True)
    hora_salida = models.DateTimeField(blank=True, null=True)
    user_entrada = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas_registradas_entrada')
    user_salida = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas_registradas_salida')
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Visita de {self.nombre_visitante} a {self.residente.nombre_completo}"


class Notificacion(models.Model):
    TIPOS = (('informativa', 'Informativa'), ('alerta', 'Alerta'), ('recordatorio', 'Recordatorio'))
    user = models.ForeignKey('usuarios.User', on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    fecha_hora = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    ruta = models.CharField(max_length=255, blank=True, null=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
