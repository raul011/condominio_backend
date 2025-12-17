from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Empleado, CargoEmpleado, EmpresaExterna
from .serializers import EmpleadoSerializer, CargoEmpleadoSerializer, EmpresaExternaSerializer

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    # Enable search
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'apellido', 'ci']

class CargoEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = CargoEmpleado.objects.all()
    serializer_class = CargoEmpleadoSerializer

class EmpresaExternaViewSet(viewsets.ModelViewSet):
    queryset = EmpresaExterna.objects.all()
    serializer_class = EmpresaExternaSerializer
