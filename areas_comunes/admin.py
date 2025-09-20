from django.contrib import admin
from .models import AreaComun, Inventario, VerificacionInventario, Reserva
# Register your models here.
admin.site.register(AreaComun)
admin.site.register(Inventario)
admin.site.register(VerificacionInventario)
admin.site.register(Reserva)