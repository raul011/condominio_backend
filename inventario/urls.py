from rest_framework.routers import DefaultRouter
from .views import CategoriaInventarioViewSet

router = DefaultRouter()
router.register(r'categorias-inventario', CategoriaInventarioViewSet)

urlpatterns = router.urls
