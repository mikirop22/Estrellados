from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
@login_required
def camara_view(request):
    return render(request, 'camara/camara.html')

