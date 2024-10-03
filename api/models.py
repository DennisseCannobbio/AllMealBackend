from django.db import models

# Create your models here.
from django.db import models
from datetime import date

# Create your models here.
class Menu(models.Model):
    entrada = models.CharField(max_length=100)
    plato_fondo = models.CharField(max_length=100)
    postre = models.CharField(max_length=100)
    fecha = models.CharField(max_length=12)
    
    def __str__(self) -> str:
        return super().__str__()
    
class Pedido(models.Model):
    fecha = models.CharField(max_length=12)
    nombre_cliente = models.CharField(max_length=100)
    menus = models.ManyToManyField(Menu,  related_name='pedidos')
    

class MenuResponse(models.Model):
    response_text = models.TextField()
    user_id = models.CharField(max_length=255)
    menu_id = models.IntegerField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response from {self.user_id}: {self.response_text}'

    
class Usuario(models.Model):
    usuario = models.CharField(max_length=100)
    contraseña = models.CharField(max_length=15)
    pedidos = models.ManyToManyField(Pedido, blank=True)
    
    