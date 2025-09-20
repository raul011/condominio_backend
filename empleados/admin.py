from django.contrib import admin
from .models import Empleado, CargoEmpleado, EmpresaExterna
# Register your models here.
admin.site.register(Empleado)
admin.site.register(CargoEmpleado)
admin.site.register(EmpresaExterna)