from rest_framework.routers import DefaultRouter
from .views import ComunicadoViewSet

router = DefaultRouter()
router.register(r'comunicados', ComunicadoViewSet)

urlpatterns = router.urls
