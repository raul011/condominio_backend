from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Comunicado, ComunicadoResidente
from .serializers import ComunicadoSerializer
from residentes.models import Residente

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

    def perform_create(self, serializer):
        comunicado = serializer.save()
        residentes = Residente.objects.all()
        comunicado_residentes = [
            ComunicadoResidente(comunicado=comunicado, residente=residente)
            for residente in residentes
        ]
        ComunicadoResidente.objects.bulk_create(comunicado_residentes)

