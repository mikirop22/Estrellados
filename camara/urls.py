from django.urls import path
from .views import camara_view

urlpatterns = [
    path('camara/', camara_view, name='camara'),  # Ruta para la cámara
]
