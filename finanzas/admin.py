from django.contrib import admin
from .models import Cuota, Pago, Multa, TipoCuota
# Register your models here.
admin.site.register(Cuota)
admin.site.register(Pago)
admin.site.register(Multa)
admin.site.register(TipoCuota)
