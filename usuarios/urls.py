from django.urls import path
from .views import login_view,registro_view, home
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('login')),  # Redirige a login si se accede a la raíz
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
    path('registro/', registro_view, name='registro'),  # Ruta para el registro
]
