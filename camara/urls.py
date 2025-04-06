from django.urls import path
from .views import camara_view, procesar_imagen

urlpatterns = [
    path('camara/', camara_view, name='camara'),  # Ruta para la cámara
    path('procesar_imagen/', procesar_imagen, name='procesar_imagen'),
]
