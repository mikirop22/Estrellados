from django.urls import path
from .views import login_view, home
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
]
