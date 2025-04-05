from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import torch
from ultralytics import YOLO
from io import BytesIO
from PIL import Image
import base64
import json

# Vista protegida para acceder a la cámara
@login_required
def camara_view(request):
    return render(request, 'camara/camara.html')

# Cargar el modelo YOLOv8 con tus pesos
model = YOLO('static/models/yolov8n.pt')  # Asegúrate de que esta ruta sea correcta

# Vista para procesar la imagen capturada desde el frontend
@csrf_exempt
def procesar_imagen(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            img_str = image_data.split(',')[1]  # Eliminar encabezado base64
            img_bytes = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")

            # Procesar la imagen con YOLOv8
            results = model(img)[0]  # Obtener el primer resultado del batch

            detections = []
            for box in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = box
                detections.append({
                    'clase': model.names[int(class_id)],
                    'confianza': float(score),
                    'coordenadas': [int(x1), int(y1), int(x2), int(y2)]
                })

            return JsonResponse({'detecciones': detections})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=400)
