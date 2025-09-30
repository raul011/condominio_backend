from django.db import models
from django.utils import timezone

class TipoCuota(models.Model):
    nombre = models.CharField(max_length=100)
    frecuencia = models.CharField(max_length=50, help_text="Ej: 'mensual', 'extraordinaria'")
    editable = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Cuota(models.Model):
    ESTADOS = (('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('vencida', 'Vencida'))
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_emision = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    residente = models.ForeignKey('residentes.Residente', on_delete=models.CASCADE, related_name='cuotas')
    tipo_cuota = models.ForeignKey(TipoCuota, on_delete=models.PROTECT, related_name='cuotas')
    user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, null=True, related_name='cuotas_creadas')
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cuota {self.titulo} para {self.residente.nombre_completo}"


class Multa(models.Model):
    ESTADOS = (('pendiente', 'Pendiente'), ('pagada', 'Pagada'))
    motivo = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_emision = models.DateTimeField(default=timezone.now)
    fecha_limite = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    residente = models.ForeignKey('residentes.Residente', on_delete=models.CASCADE, related_name='multas')
    empleado = models.ForeignKey('empleados.Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name='multas_emitidas')
    cuota = models.ForeignKey(Cuota, on_delete=models.SET_NULL, null=True, blank=True, related_name='multas')

    def __str__(self):
        return f"Multa por {self.motivo} a {self.residente.nombre_completo}"


class Pago(models.Model):
    TIPOS = (('cuota', 'Cuota'),('multa', 'Multa'),('reserva', 'Reserva'),)
    METODOS = (('efectivo', 'Efectivo'), ('qr', 'QR'), ('tarjeta', 'Tarjeta'))
    ESTADOS = (('completado', 'Completado'), ('pendiente', 'Pendiente'), ('fallido', 'Fallido'))
    tipo = models.CharField(max_length=20, choices=TIPOS)
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    multa = models.ForeignKey(Multa, on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    reserva = models.ForeignKey('areas_comunes.Reserva', on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(default=timezone.now)
    metodo = models.CharField(max_length=50, choices=METODOS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='completado')
    comprobante = models.FileField(upload_to='pagos/comprobantes/', blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, null=True, related_name='pagos_registrados')

    def __str__(self):
        concepto = self.get_tipo_display()
        return f"{concepto} - {self.monto_pagado} ({self.fecha_pago.date()})"