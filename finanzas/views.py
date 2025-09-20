from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Cuota, Pago, Multa, TipoCuota
from .serializers import CuotaSerializer, PagoSerializer, MultaSerializer, TipoCuotaSerializer

class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class MultaViewSet(viewsets.ModelViewSet):
    queryset = Multa.objects.all()
    serializer_class = MultaSerializer

class TipoCuotaViewSet(viewsets.ModelViewSet):
    queryset = TipoCuota.objects.all()
    serializer_class = TipoCuotaSerializer
