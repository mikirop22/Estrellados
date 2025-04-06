from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import supervision as sv
from inference import get_model


# Vista protegida para acceder a la cámara
@login_required
def camara_view(request):
    return render(request, 'camara/camara.html')

# Cargar tu modelo desde Roboflow o donde esté alojado
model = get_model(model_id="repte-3-estrellados/4", api_key="U0o3fhahNXrb9BUh72IO")

# Anotadores de Supervision
bounding_box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Procesar imágenes recibidas desde el frontend
@csrf_exempt
def procesar_imagen(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            img_str = image_data.split(',')[1]  # Eliminar encabezado base64
            img_bytes = base64.b64decode(img_str)

            # Convertir a imagen PIL y luego a array NumPy (OpenCV)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Inferencia con tu modelo
            results = model.infer(frame)[0]

            # Convertir a detecciones y anotar
            detections = sv.Detections.from_inference(results)
            frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
            frame = label_annotator.annotate(scene=frame, detections=detections)

            # Codificar imagen anotada a base64 para devolverla al frontend
            _, buffer = cv2.imencode('.jpg', frame)
            encoded_image = base64.b64encode(buffer).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{encoded_image}"

            return JsonResponse({'image': image_data_url})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=400)
