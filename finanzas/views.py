from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
# Create your views here.
from rest_framework import viewsets
from .models import Cuota, Pago, Multa, TipoCuota
from .serializers import CuotaSerializer, PagoSerializer, MultaSerializer, TipoCuotaSerializer, CuotaCreateForAllSerializer
from rest_framework.response import Response
import stripe
from usuarios.models import User
from django.conf import settings

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


class CuotaCreateForAllUsersView(APIView):
    def post(self, request):
        # 1️⃣ Usamos el serializer de entrada
        serializer = CuotaCreateForAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 2️⃣ Obtenemos el tipo de cuota
        tipo_cuota = TipoCuota.objects.get(id=data['tipo_cuota_id'])

        # 3️⃣ Obtenemos el usuario que está creando las cuotas
        user = request.user if request.user.is_authenticated else None

        # 4️⃣ Solo usuarios que tengan residente asociado
        usuarios = User.objects.filter(residente__isnull=False)
        cuotas_creadas = []

        # 5️⃣ Crear una cuota para cada usuario
        for u in usuarios:
            cuota = Cuota.objects.create(
                titulo=data['titulo'],
                descripcion=data.get('descripcion', ''),
                fecha_emision=data['fecha_emision'],
                fecha_vencimiento=data['fecha_vencimiento'],
                monto=data['monto'],
                estado=data['estado'],
                residente=u.residente,  # asigna el residente relacionado
                tipo_cuota=tipo_cuota,
                user=user,
                observacion=data.get('observacion', '')
            )
            cuotas_creadas.append(cuota)

        # 6️⃣ Devolvemos la respuesta con los datos completos usando CuotaSerializer
        return Response(
            CuotaSerializer(cuotas_creadas, many=True).data,
            status=status.HTTP_201_CREATED
        )

class CuotasPorUsuarioIdView(APIView):
    """
    Devuelve todas las cuotas de un usuario a partir de su ID.
    """
    def get(self, request, user_id):
        try:
            usuario = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not usuario.residente:
            return Response({"detail": "Usuario no tiene residente asociado."}, status=status.HTTP_400_BAD_REQUEST)

        cuotas = Cuota.objects.filter(residente=usuario.residente).order_by('fecha_emision')
        serializer = CuotaSerializer(cuotas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



        
stripe.api_key = settings.STRIPE_SECRET_KEY  # Debes tener esto en settings

class CreatePaymentIntentView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            amount = float(request.data.get("amount", 0))
            if amount <= 0:
                return Response({"error": "Monto inválido"}, status=400)

            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe trabaja en centavos
                currency='usd',
                payment_method_types=['card'],
            )
            return Response({"clientSecret": intent.client_secret})
        except Exception as e:
            return Response({"error": str(e)}, status=500)