from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cliente(models.Model):
    nombre_usuario = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=100)


class Resena(models.Model):
    CALIFICACIONES = [(valor, f'{valor} estrellas') for valor in range(1, 6)]

    nombre = models.CharField(max_length=80)
    calificacion = models.PositiveSmallIntegerField(choices=CALIFICACIONES)
    comentario = models.TextField(max_length=700)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.nombre} — {self.calificacion}/5'
    
class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(max_length=1000)
    precio = models.IntegerField()
    imagen = models.CharField(max_length=200, null=True)
    stock = models.PositiveIntegerField()
    
    def __str__(self):
        return self.nombre


