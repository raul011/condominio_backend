from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Comunicado, ComunicadoResidente
from .serializers import ComunicadoSerializer, ComunicadoResidenteSerializer
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


from rest_framework import generics

class ComunicadoResidenteListView(generics.ListAPIView):
    serializer_class = ComunicadoResidenteSerializer

    def get_queryset(self):
        """
        This view returns a list of all ComunicadoResidente for a specific resident
        determined by the `residente_id` portion of the URL.
        """
        residente_id = self.kwargs['residente_id']
        return ComunicadoResidente.objects.filter(residente__id=residente_id)


class ComunicadoResidentesListByComunicadoView(generics.ListAPIView):
    serializer_class = ComunicadoResidenteSerializer

    def get_queryset(self):
        """
        This view returns a list of all ComunicadoResidente for a specific comunicado
        determined by the `comunicado_id` portion of the URL.
        """
        comunicado_id = self.kwargs['comunicado_id']
        return ComunicadoResidente.objects.filter(comunicado__id=comunicado_id)

