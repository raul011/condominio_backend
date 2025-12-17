import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

# Import all necessary models
from usuarios.models import User
from empleados.models import Empleado, CargoEmpleado
from residentes.models import Residente, Unidad
from finanzas.models import Multa
from areas_comunes.models import AreaComun, Inventario
from inventario.models import CategoriaInventario
from tareas.models import Tarea

class Command(BaseCommand):
    help = 'Seeds the database with realistic dummy data for all modules.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Clean up existing data to prevent duplicates
        self.stdout.write('Deleting existing data...')
        Tarea.objects.all().delete()
        Inventario.objects.all().delete()
        CategoriaInventario.objects.all().delete()
        Multa.objects.all().delete()
        AreaComun.objects.all().delete()
        Unidad.objects.all().delete()
        # Must delete User links before deleting the objects themselves
        User.objects.update(residente=None, empleado=None)
        Residente.objects.all().delete()
        Empleado.objects.all().delete()
        CargoEmpleado.objects.all().delete()
        User.objects.all().filter(is_superuser=False).delete()

        # Initialize Faker
        fake = Faker('es_ES') # Use Spanish localization

        # --- 1. Create Users ---
        self.stdout.write('Creating users...')
        admin_user, _ = User.objects.get_or_create(
            username='admin', 
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@condominio.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.save()

        users = [admin_user]
        self.stdout.write('Creating 250 users...')
        for _ in range(250):
            first_name = fake.first_name()
            last_name = fake.last_name()
            # Ensure username is unique
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'password':'password123',
                    'first_name':first_name,
                    'last_name':last_name,
                    'email':fake.email()
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)

        # --- 2. Create Cargos (Positions) ---
        self.stdout.write('Creating cargos...')
        cargos_data = ['Gerente de Condominio', 'Guardia de Seguridad', 'Personal de Mantenimiento', 'Jardinero', 'Contador', 'Recepcionista']
        cargos = [CargoEmpleado.objects.create(cargo=c) for c in cargos_data]

        # --- 3. Create Empleados (Employees) ---
        self.stdout.write('Creating 100 empleados...')
        empleados = []
        for user in users[1:101]: # Use 100 non-admin users
            empleado = Empleado.objects.create(
                nombre=user.first_name,
                apellido=user.last_name,
                ci=fake.unique.ssn(), # Using ssn for more unique values
                telefono=fake.phone_number(),
                direccion=fake.address(),
                cargo=random.choice(cargos)
            )
            user.empleado = empleado
            user.save()
            empleados.append(empleado)

        # --- 4. Create Residentes (Residents) ---
        self.stdout.write('Creating 150 residentes...')
        residentes = []
        for user in users[101:]: # Use the rest of the users
            residente = Residente.objects.create(
                nombre=user.first_name,
                apellido=user.last_name,
                ci=fake.unique.ssn(),
                email=user.email,
                tipo_residente=random.choice(['Propietario', 'Inquilino'])
            )
            user.residente = residente
            user.save()
            residentes.append(residente)

        # --- 5. Create Unidades (Units) ---
        self.stdout.write('Creating 150 unidades...')
        for i, res in enumerate(residentes):
            Unidad.objects.create(
                codigo=f"{random.choice(['A', 'B', 'C', 'D'])}-{101 + i}",
                placa=f"{random.randint(1000, 9999)}-{fake.lexify(text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
                marca=random.choice(['Toyota', 'Nissan', 'Kia', 'Suzuki', 'Hyundai']),
                estado='activa',
                residente=res
            )
        
        # --- 6. Create Areas Comunes ---
        self.stdout.write('Creating 10 areas comunes...')
        AreaComun.objects.all().delete() # Clear previous ones first
        areas_data = [
            {'nombre': 'Piscina', 'monto': 100.00, 'estado': 'disponible'},
            {'nombre': 'Gimnasio', 'monto': 50.00, 'estado': 'disponible'},
            {'nombre': 'Salón de Eventos Principal', 'monto': 500.00, 'estado': 'en_mantenimiento'},
            {'nombre': 'Parrillero A', 'monto': 75.00, 'estado': 'disponible'},
            {'nombre': 'Parrillero B', 'monto': 75.00, 'estado': 'no_disponible'},
            {'nombre': 'Cancha de Tenis', 'monto': 80.00, 'estado': 'disponible'},
            {'nombre': 'Cancha de Fútbol 5', 'monto': 120.00, 'estado': 'disponible'},
            {'nombre': 'Sala de Cine', 'monto': 150.00, 'estado': 'disponible'},
            {'nombre': 'Sauna', 'monto': 40.00, 'estado': 'en_mantenimiento'},
            {'nombre': 'Salón de Eventos Pequeño', 'monto': 250.00, 'estado': 'disponible'},
        ]
        areas = [AreaComun.objects.create(**data) for data in areas_data]

        # --- 7. Create Multas (Fines) ---
        self.stdout.write('Creating 100 multas...')
        for _ in range(100):
            Multa.objects.create(
                motivo=random.choice(['Estacionamiento indebido', 'Ruido excesivo', 'Basura en áreas comunes', 'Mascota sin correa', 'Daño a propiedad común']),
                monto=random.uniform(50.0, 300.0),
                fecha_limite=fake.future_date(end_date="+60d"),
                estado=random.choice(['pendiente', 'pagada']),
                residente=random.choice(residentes)
            )

        # --- 8. Create Inventory Categories and Items ---
        self.stdout.write('Creating 150 items de inventario...')
        cat_inv_data = [
            'Herramientas Manuales', 'Herramientas Eléctricas', 'Equipo de Jardinería', 'Mobiliario de Oficina', 
            'Productos de Limpieza', 'Equipo de Seguridad', 'Señalización', 'Material de Plomería',
            'Material Eléctrico', 'Repuestos de Piscina', 'Decoración', 'Equipo de Gimnasio',
            'Suministros de Baño', 'Utensilios de Cocina (Salón)', 'Equipo Audiovisual'
        ]
        categorias_inv = [CategoriaInventario.objects.create(nombre=c, descripcion=f"Categoría para {c}") for c in cat_inv_data]
        
        for cat in categorias_inv:
            for i in range(10): # 10 items per category
                Inventario.objects.create(
                    nombre=f"{cat.nombre} Item #{i+1}",
                    descripcion=fake.sentence(),
                    estado=random.choice(['Bueno', 'Regular', 'Necesita Reparación', 'En Desuso']),
                    fecha_adquisicion=fake.past_date(),
                    tipo_adquisicion=random.choice(['Compra', 'Donación']),
                    valor_estimado=random.uniform(50.0, 3000.0),
                    ubicacion=f"Almacén {random.randint(1,5)}",
                    categoria=cat,
                    user=admin_user
                )

        # --- 9. Create Tareas (Tasks) ---
        self.stdout.write('Creating 100 tareas...')
        for _ in range(100):
            Tarea.objects.create(
                titulo=fake.sentence(nb_words=5).replace('.', ''),
                descripcion=fake.paragraph(nb_sentences=4),
                fecha_limite=fake.future_date(end_date="+90d"),
                estado=random.choice(['Pendiente', 'En Progreso', 'Completada', 'Cancelada']),
                prioridad=random.choice(['Baja', 'Media', 'Alta']),
                empleado_asignado=random.choice(empleados),
                creado_por=admin_user
            )

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
