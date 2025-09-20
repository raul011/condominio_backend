from django.contrib import admin
from .models import Residente, Unidad, Visita, Notificacion
# Register your models here.
admin.site.register(Residente)
admin.site.register(Unidad)
admin.site.register(Visita)
admin.site.register(Notificacion)