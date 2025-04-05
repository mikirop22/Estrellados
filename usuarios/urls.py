from django.urls import path
from .views import login_view,registro_view, home
from camara.views import camara_view
from django.shortcuts import redirect


urlpatterns = [
    path('', home, name='home'),  # Redirigir a 'home' en la raíz
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('camara/', camara_view, name='camara'),
]
