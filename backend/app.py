from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import cv2
import torch
import json
import numpy as np
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

app = Flask(__name__)
CORS(app)  # Habilitar CORS

# Directorios
VIDEO_DIR = 'videos'
METADATA_FILE = 'metadata.json'

# Asegurarse de que los directorios existen
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# Cargar o inicializar metadatos
if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
else:
    metadata = {}

# Cargar modelos
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Cargar modelo YOLOv5
model_yolo = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model_yolo.to(device)

# Cargar modelo BLIP
processor_blip = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model_blip = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
model_blip.to(device)

# Rango de colores para detección
color_ranges = {
    'rojo': ([0, 70, 50], [10, 255, 255]),
    'verde': ([36, 25, 25], [86, 255, 255]),
    'azul': ([94, 80, 2], [126, 255, 255]),
    # Agregar más colores si es necesario
}

def obtener_color_dominante(imagen):
    hsv_imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    for color, (lower, upper) in color_ranges.items():
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(hsv_imagen, lower, upper)
        porcentaje = (cv2.countNonZero(mask) / (imagen.size / 3)) * 100  # Dividido por 3 por los canales de color
        if porcentaje > 5:  # Umbral para considerar el color dominante
            return color
    return 'desconocido'

def describir_imagen(imagen):
    # Convertir imagen de OpenCV (BGR) a PIL (RGB)
    imagen_pil = Image.fromarray(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))
    inputs = processor_blip(imagen_pil, return_tensors="pt").to(device)
    out = model_blip.generate(**inputs)
    descripcion = processor_blip.decode(out[0], skip_special_tokens=True)
    return descripcion

def procesar_video(ruta_video):
    etiquetas = set()
    cap = cv2.VideoCapture(ruta_video)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_process = min(frame_count, 30)
    for i in range(frames_to_process):
        ret, frame = cap.read()
        if not ret:
            break
        frame_resized = cv2.resize(frame, (640, 360))
        # Detección de objetos con YOLOv5
        results = model_yolo(frame_resized)
        detections = results.xyxy[0]
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            etiqueta_obj = model_yolo.names[int(cls)]
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            objeto_imagen = frame_resized[y1:y2, x1:x2]
            color = obtener_color_dominante(objeto_imagen)
            etiqueta_final = f"{etiqueta_obj} {color}" if color != 'desconocido' else etiqueta_obj
            etiquetas.add(etiqueta_final.lower())
        # Descripción de la imagen con BLIP
        descripcion = describir_imagen(frame_resized)
        etiquetas.update(descripcion.lower().split())
    cap.release()
    return list(etiquetas)

def actualizar_metadatos(nombre_video, etiquetas):
    metadata[nombre_video] = etiquetas
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

@app.route('/api/subir', methods=['POST'])
def subir_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún video.'}), 400
    archivo = request.files['video']
    nombre_video = archivo.filename
    ruta_destino = os.path.join(VIDEO_DIR, nombre_video)
    archivo.save(ruta_destino)
    etiquetas = procesar_video(ruta_destino)
    actualizar_metadatos(nombre_video, etiquetas)
    return jsonify({'mensaje': 'Video subido y procesado con éxito.', 'etiquetas': etiquetas}), 200

@app.route('/api/buscar')
def buscar_videos():
    consulta = request.args.get('consulta', '').lower()
    resultados = []
    if consulta:
        for nombre_video, etiquetas in metadata.items():
            coincidencias = sum(1 for etiqueta in etiquetas if consulta in etiqueta)
            if coincidencias > 0:
                resultados.append({'nombre': nombre_video, 'coincidencias': coincidencias})
        resultados.sort(key=lambda x: x['coincidencias'], reverse=True)
    return jsonify(resultados[:10])

@app.route('/videos/<nombre_video>')
def servir_video(nombre_video):
    return send_from_directory(VIDEO_DIR, nombre_video)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
