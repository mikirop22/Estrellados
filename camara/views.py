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
import math

# Parámetros para el conteo
DIST_THRESHOLD = 30
MAX_MISSED_FRAMES = 5

# Vista protegida para acceder a la cámara
@login_required
def camara_view(request):
    return render(request, 'camara/camara.html')

# Cargar tu modelo desde Roboflow
model = get_model(model_id="repte-3-estrellados/4", api_key="U0o3fhahNXrb9BUh72IO")

# Anotadores de Supervision
bounding_box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Mapeo manual de índices a nombres
class_names = {
    0: "box_estrella",
    1: "box_veri",
    2: "person_handfree",
    3: "person_holding",
    4: "rack_ver",
    5: "rack_ver",
}

# Estado global para las detecciones activas y contadores
active_detections = []  # (cx, cy, label, last_seen_frame)
rack_veri_count = 0
box_estrella_count = 0
frame_count = 0

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Procesar imágenes recibidas desde el frontend
@csrf_exempt
def procesar_imagen(request):
    global active_detections, rack_veri_count, box_estrella_count, frame_count

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

            # Incrementar contador de frames
            frame_count += 1

            # Inferencia con el modelo
            results = model.infer(frame)[0]
            detections = sv.Detections.from_inference(results)

            # Anotar fotograma
            annotated_frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
            annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections)

            # Definir región de conteo (mitad derecha de la imagen)
            width = frame.shape[1]
            line_x = width // 2

            # Lista de detecciones actuales en la región: (cx, cy, label)
            current_detections = []

            if detections.xyxy is not None and len(detections.xyxy) > 0:
                for i, box in enumerate(detections.xyxy):
                    x_min, y_min, x_max, y_max = box
                    cx = (x_min + x_max) / 2
                    cy = (y_min + y_max) / 2

                    # Obtener label usando detections.class_id y el mapeo
                    label_index = detections.class_id[i] if hasattr(detections, "class_id") and detections.class_id is not None else None
                    label = class_names.get(label_index, "Unknown") if label_index is not None else "Unknown"

                    # Ignorar ciertos labels
                    if label in ['person_holding', 'person_handfree']:
                        continue

                    # Verificar si está en la región de conteo
                    if line_x <= cx <= line_x + 30:
                        current_detections.append((cx, cy, label))

            # Procesar detecciones actuales: verificar si son nuevas
            for (cx, cy, label) in current_detections:
                matched = False
                for idx, (ax, ay, a_label, last_seen) in enumerate(active_detections):
                    if label == a_label and distance((cx, cy), (ax, ay)) < DIST_THRESHOLD:
                        matched = True
                        active_detections[idx] = (cx, cy, label, frame_count)
                        break
                if not matched:
                    # Detección nueva: incrementar contadores
                    if label == "rack_ver" and rack_veri_count < 3:  # Límite según frontend
                        rack_veri_count += 1
                    elif label == "box_estrella" and box_estrella_count < 1:  # Límite según frontend
                        box_estrella_count += 1
                    # Agregar a detecciones activas
                    active_detections.append((cx, cy, label, frame_count))

            # Eliminar detecciones activas no vistas recientemente
            active_detections = [
                (ax, ay, a_label, last_seen)
                for (ax, ay, a_label, last_seen) in active_detections
                if frame_count - last_seen <= MAX_MISSED_FRAMES
            ]

            # Codificar imagen anotada a base64 para devolverla al frontend
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            encoded_image = base64.b64encode(buffer).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{encoded_image}"

            # Preparar respuesta con la imagen y los contadores
            response_data = {
                'image': image_data_url,
                'detections': [
                    {'type': 'rack_veri', 'count': rack_veri_count},
                    {'type': 'box_estrella', 'count': box_estrella_count}
                ]
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=400)