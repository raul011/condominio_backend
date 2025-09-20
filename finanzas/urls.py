from rest_framework.routers import DefaultRouter
from .views import CuotaViewSet, PagoViewSet, MultaViewSet, TipoCuotaViewSet

router = DefaultRouter()
router.register(r'cuotas', CuotaViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'multas', MultaViewSet)
router.register(r'tipos-cuota', TipoCuotaViewSet)

urlpatterns = router.urls
