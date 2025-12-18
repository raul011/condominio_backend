from rest_framework.routers import DefaultRouter
from .views import RegistroAccesoViewSet

router = DefaultRouter()
router.register(r'registros-accesos', RegistroAccesoViewSet, basename='registro_acceso')

urlpatterns = router.urls
