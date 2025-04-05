from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # Redirige a otra vista
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "usuarios/login.html")

def registro_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        # Verificar si las contraseñas coinciden
        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "usuarios/registro.html")

        # Crear un nuevo usuario
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
            return render(request, "usuarios/registro.html")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Usuario creado exitosamente. Ahora puedes iniciar sesión.")
        return redirect("login")  # Redirige al login

    return render(request, "usuarios/registro.html")

@login_required
def home(request):
    return HttpResponse("Bienvenido, estás logueado.")

