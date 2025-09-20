from django.db import models
from django.utils import timezone

class TipoGasto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Gasto(models.Model):
    tipo_gasto = models.ForeignKey(TipoGasto, on_delete=models.PROTECT, related_name='gastos')
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.concepto} - {self.monto}"
