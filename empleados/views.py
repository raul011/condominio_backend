from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Empleado, CargoEmpleado, EmpresaExterna
from .serializers import EmpleadoSerializer, CargoEmpleadoSerializer, EmpresaExternaSerializer

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer

class CargoEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = CargoEmpleado.objects.all()
    serializer_class = CargoEmpleadoSerializer

class EmpresaExternaViewSet(viewsets.ModelViewSet):
    queryset = EmpresaExterna.objects.all()
    serializer_class = EmpresaExternaSerializer
