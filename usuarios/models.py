from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Usuario extendido que se relaciona 1-a-1 con Residente o Empleado.
    """
    residente = models.OneToOneField('residentes.Residente', on_delete=models.SET_NULL, null=True, blank=True, related_name='user')
    empleado = models.OneToOneField('empleados.Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name='user')

    def __str__(self):
        return self.username
