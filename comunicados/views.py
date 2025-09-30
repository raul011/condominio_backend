from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Comunicado
from .serializers import ComunicadoSerializer

#class ComunicadoViewSet(viewsets.ModelViewSet):
#    queryset = Comunicado.objects.all()
#    serializer_class = ComunicadoSerializer
class ComunicadoViewSet(viewsets.ModelViewSet):
    queryset = Comunicado.objects.all()  
    serializer_class = ComunicadoSerializer

    def get_queryset(self):
        queryset = Comunicado.objects.all()
        tipo = self.request.query_params.get('tipo')  # ?tipo=urgente
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset

