from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets
from .models import Residente, Unidad, Visita, Notificacion
from .serializers import ResidenteSerializer, UnidadSerializer, VisitaSerializer, NotificacionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class ResidenteViewSet(viewsets.ModelViewSet):
    queryset = Residente.objects.all()
    serializer_class = ResidenteSerializer

class UnidadViewSet(viewsets.ModelViewSet):
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer

    @action(detail=False, methods=['get'], url_path='placas')
    def listar_placas(self, request):
        # Obtener todas las placas no nulas
        placas = list(self.queryset.exclude(placa__isnull=True).exclude(placa="").values_list('placa', flat=True))
        return Response(placas)

class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
