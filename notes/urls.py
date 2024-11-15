from django.urls import path
from . import views

urlpatterns = [
    path('', views.iniciar_sesion, name='iniciar_sesion'),
    path('crear_cuenta/', views.crear_cuenta, name='crear_cuenta'),
    path('usuario/', views.usuario, name='usuario'),
    path('agregar_nota/', views.agregar_nota, name='agregar_nota'),
    path('cerrar_sesion/', views.cerrar_sesion, name="cerrar_sesion"),
    path('nota/<uuid:nota_id>/', views.ver_nota, name='ver_nota'),
]
