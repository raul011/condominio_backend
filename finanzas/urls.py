from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CuotaViewSet, PagoViewSet, MultaViewSet, TipoCuotaViewSet, CreatePaymentIntentView, CuotaCreateForAllUsersView, CuotasPorUsuarioIdView

router = DefaultRouter()
router.register(r'cuotas', CuotaViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'multas', MultaViewSet)
router.register(r'tipos-cuota', TipoCuotaViewSet)

urlpatterns = [
    # Esta es la nueva línea que añade el endpoint para Stripe
    path('intent/', CreatePaymentIntentView.as_view()),
    path('cuotas/crear-todos-expensas/', CuotaCreateForAllUsersView.as_view()),
    path('cuotas/mis-cuotas/<int:user_id>/', CuotasPorUsuarioIdView.as_view()),

]

urlpatterns += router.urls
