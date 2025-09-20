from django.db import models

class CargoEmpleado(models.Model):
    cargo = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=20, default='activo')

    def __str__(self):
        return self.cargo


class Empleado(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    ci = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.ForeignKey(CargoEmpleado, on_delete=models.PROTECT, related_name='empleados')

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return self.nombre_completo


class EmpresaExterna(models.Model):
    nombre = models.CharField(max_length=255)
    servicio = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
