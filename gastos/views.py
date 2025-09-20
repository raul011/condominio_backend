from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Gasto, TipoGasto
from .serializers import GastoSerializer, TipoGastoSerializer

class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer

class TipoGastoViewSet(viewsets.ModelViewSet):
    queryset = TipoGasto.objects.all()
    serializer_class = TipoGastoSerializer
