from django.db import models

class AreaComun(models.Model):
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, default='disponible')

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=50)
    fecha_adquisicion = models.DateField()
    tipo_adquisicion = models.CharField(max_length=50)
    valor_estimado = models.DecimalField(max_digits=10, decimal_places=2)
    vida_util = models.PositiveIntegerField(help_text="En años", blank=True, null=True)
    valor_residual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_baja = models.DateField(blank=True, null=True)
    motivo_baja = models.CharField(max_length=255, blank=True, null=True)
    ubicacion = models.CharField(max_length=255)
    categoria = models.ForeignKey('inventario.CategoriaInventario', on_delete=models.PROTECT, related_name='inventarios')
    user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, null=True, related_name='inventarios_registrados')
    area_comun = models.ForeignKey(AreaComun, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventarios')

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADOS = (('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'))
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observacion = models.TextField(blank=True, null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    area_comun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, related_name='reservas')
    residente = models.ForeignKey('residentes.Residente', on_delete=models.CASCADE, related_name='reservas')

    def __str__(self):
        return f"Reserva de {self.area_comun.nombre} por {self.residente.nombre_completo}"


class VerificacionInventario(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='verificaciones')
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='verificaciones')
    estado = models.CharField(max_length=50)
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('reserva', 'inventario')
