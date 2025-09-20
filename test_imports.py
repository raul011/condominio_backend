import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_condominio.settings')
django.setup()

# Ahora hacer los imports
try:
    
    from residentes.serializers import ResidenteSerializer
    from empleados.serializers import EmpleadoSerializer
    print("✅ Todos los imports funcionan correctamente")
except ImportError as e:
    print(f"❌ Error de import: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")