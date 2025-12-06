import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_condominio.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from comunicados.views import ComunicadoViewSet
from comunicados.models import Comunicado, ComunicadoResidente
from usuarios.models import User

# Setup
try:
    user = User.objects.first()
    if not user:
        print("No user found, creating one...")
        user = User.objects.create(username='test_script_user', password='password')
    else:
        print(f"Using user: {user.username}")

    factory = APIRequestFactory()
    view = ComunicadoViewSet.as_view({'post': 'create'})

    # Make request
    data = {
        'titulo': 'Test Script Comunicado',
        'contenido': 'Content',
        'tipo': 'informativa',
        'usuario': user.id
    }
    request = factory.post('/api/comunicados/', data, format='json')
    force_authenticate(request, user=user)

    # Execute
    print("Sending request to view...")
    response = view(request)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 201:
        comunicado_id = response.data['id']
        count = ComunicadoResidente.objects.filter(comunicado_id=comunicado_id).count()
        print(f"Comunicado created with ID: {comunicado_id}")
        print(f"ComunicadoResidente tuples created: {count}")
    else:
        print(f"Failed to create comunicado: {response.data}")

except Exception as e:
    print(f"An error occurred: {e}")
