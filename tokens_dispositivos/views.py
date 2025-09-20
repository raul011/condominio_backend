from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import DeviceToken
from .serializers import DeviceTokenSerializer, UserTokensSerializer
from usuarios.models import User

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_token(request):
    """
    Guarda o actualiza un token de dispositivo para el usuario autenticado.
    Si el token ya existe, se asegura de que esté activo y asociado al usuario actual.
    """
    token = request.data.get('token')
    
    if not token:
        return Response(
            {'error': 'El campo "token" es requerido.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Usar update_or_create para manejar la lógica de creación/actualización de forma atómica.
    # El token se asocia siempre con el usuario que hace la petición (request.user).
    device_token, created = DeviceToken.objects.update_or_create(
        token=token,
        defaults={'user': request.user, 'is_active': True}
    )
    
    status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    serializer = DeviceTokenSerializer(device_token)
    return Response(serializer.data, status=status_code)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_token(request):
    """
    Desactiva un token de dispositivo (ej. al cerrar sesión).
    """
    token = request.data.get('token')
    if not token:
        return Response({'error': 'El campo "token" es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        device_token = DeviceToken.objects.get(token=token)
        # Solo el dueño del token puede desactivarlo
        if device_token.user != request.user:
            return Response({'error': 'No tienes permiso para modificar este token.'}, status=status.HTTP_403_FORBIDDEN)
        
        device_token.is_active = False
        device_token.save()
        return Response({'detail': 'Token desactivado correctamente.'}, status=status.HTTP_200_OK)
    except DeviceToken.DoesNotExist:
        return Response(
            {'error': 'Token no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_tokens(request):
    """
    Obtiene todos los tokens activos para el usuario autenticado.
    """
    tokens = DeviceToken.objects.filter(user=request.user, is_active=True).values_list('token', flat=True)
    
    serializer = UserTokensSerializer({'tokens': list(tokens)})
    return Response(serializer.data, status=status.HTTP_200_OK)
