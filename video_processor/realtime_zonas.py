import cv2
import threading
import numpy as np
import requests
import time
from PIL import Image
from shapely.geometry import Point, Polygon  # pip install shapely
from onnxruntime_predict import ONNXRuntimeObjectDetection

MODEL_FILENAME = "model.onnx"
LABELS_FILENAME = "labels.txt"
API_URL = "http://3.129.13.240:8000/api/fcm/send/"


ULTIMOS_ALERTAS = {}
COOLDOWN = 10  # segundos mínimos entre notificaciones por evento



# Cargar etiquetas
with open(LABELS_FILENAME, "r", encoding="utf-8") as f:
    labels = [l.strip() for l in f.readlines()]

# Cargar modelo
od_model = ONNXRuntimeObjectDetection(MODEL_FILENAME, labels)

# Lista de cámaras
CAMERAS = {
    "CAM1": "http://192.168.0.45:4747/video",
    "CAM2": "http://192.168.0.166:4747/video"
}

# Zonas restringidas por cámara (coordenadas en píxeles según resolución de cada cámara)
ZONAS = {
    "CAM1": [
        {"nombre": "entrada", "tipo": "restringido", "coords": [(150,150),(350,150),(350,350),(150,350)]},
        {"nombre": "jardin", "tipo": "permitido", "coords": [(400,200),(600,200),(600,500),(400,500)]}
    ],
    "CAM2": [
        {"nombre": "patio", "tipo": "restringido", "coords": [(50,50),(200,50),(200,250),(50,250)]}
    ]
}

def notificar_una_vez(cam_id, tag_name, zona):
    clave = (cam_id, tag_name, zona["nombre"])
    ahora = time.time()

    # Verificar si ya se notificó recientemente
    if clave in ULTIMOS_ALERTAS:
        if ahora - ULTIMOS_ALERTAS[clave] < COOLDOWN:
            return  # todavía en cooldown → no enviar

    # Actualizar último timestamp
    ULTIMOS_ALERTAS[clave] = ahora
    
    titulo = "🚨 Alerta Zona Restringida"
    mensaje = f"Se detectó {tag_name} en {zona['nombre']} ({cam_id})"
    # 🔔 Enviar notificación
    enviar_notificacion(
        user_id=1,
        title="🚨 Alerta Zona Restringida",
        message=f"Se detectó {tag_name} en {zona['nombre']} ({cam_id})",
        notification_type="alert"
    )

    crear_comunicado(
        user_id=1,
        titulo=f"{tag_name} ingreso a {zona['nombre']}",
        contenido=mensaje,
        tipo="Alerta",   # o "Alerta" si prefieres
        notificado=True
    )
def enviar_notificacion(user_id, title, message, notification_type="alert"):
    try:
        payload = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": notification_type
        }
        r = requests.post(API_URL, json=payload)
        if r.status_code == 200:
            print("✅ Notificación enviada")
        else:
            print(f"⚠️ Error al enviar notificación: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Error en la notificación: {e}")


def crear_comunicado(user_id, titulo, contenido, tipo="Aviso", notificado=True):
    """Crea un comunicado en el backend"""
    try:
        payload = {
            "titulo": titulo,
            "contenido": contenido,
            "tipo": tipo,
            "usuario": user_id,
            "fecha_publicacion": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "notificado": notificado
        }
        r = requests.post("http://3.129.13.240:8000/api/comunicados/", json=payload)
        if r.status_code in (200, 201):
            print("✅ Comunicado creado")
        else:
            print(f"⚠️ Error al crear comunicado: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Error en comunicado: {e}")




def parse_prediction(pred, frame_width, frame_height):
    if isinstance(pred, dict) and 'boundingBox' in pred:
        bbox = pred['boundingBox']
        prob = pred['probability']
        tag_name = pred.get('tagName', 'unknown')

        left, top, width, height = bbox['left'], bbox['top'], bbox['width'], bbox['height']
        x1, y1 = int(left * frame_width), int(top * frame_height)
        x2, y2 = int((left + width) * frame_width), int((top + height) * frame_height)
        return x1, y1, x2, y2, float(prob), tag_name
    return None

def punto_en_zona(cam_id, x, y):
    """Verifica si (x,y) está en una zona restringida de la cámara"""
    zonas = ZONAS.get(cam_id, [])
    for zona in zonas:
        poly = Polygon(zona["coords"])
        if poly.contains(Point(x, y)):
            return zona
    return None

def process_camera(cam_id, url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir {cam_id} en {url}")
        return

    print(f"✅ Cámara {cam_id} abierta")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ {cam_id}: no se recibió frame")
            break

        frame_height, frame_width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        try:
            predictions = od_model.predict_image(pil_image)
            for pred in predictions:
                parsed = parse_prediction(pred, frame_width, frame_height)
                if parsed is None:
                    continue
                x1, y1, x2, y2, prob, tag_name = parsed
                if prob < 0.6:
                    continue

                # Centroide del bounding box
                cx, cy = int((x1+x2)/2), int((y1+y2)/2)

                # Verificar si está en zona restringida
                zona = punto_en_zona(cam_id, cx, cy)

                color = (0, 255, 0)  # verde por defecto
                if zona and zona["tipo"] == "restringido":
                    color = (0, 0, 255)  # rojo
                    cv2.putText(frame, f"ALERTA: {tag_name} en {zona['nombre']}",
                                (x1, max(0, y1 - 20)), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 0, 255), 2)
                    #  Notificación con control de frecuencia
                    notificar_una_vez(cam_id, tag_name, zona)           

                # Dibujar bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{tag_name} {prob:.2f}",
                            (x1, max(0, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, color, 2)

                # Dibujar punto centroide
                cv2.circle(frame, (cx, cy), 5, color, -1)

        except Exception as e:
            print(f"Error en {cam_id}: {e}")

        # Dibujar zonas en el frame
        for zona in ZONAS.get(cam_id, []):
            poly = Polygon(zona["coords"])
            pts = np.array(zona["coords"], np.int32)
            pts = pts.reshape((-1, 1, 2))
            col = (0, 0, 255) if zona["tipo"] == "restringido" else (0, 255, 0)
            cv2.polylines(frame, [pts], True, col, 2)
            cv2.putText(frame, zona["nombre"], zona["coords"][0],
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)

        # Ventana con nombre de cámara
        cv2.imshow(f"{cam_id}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(f"{cam_id}")

# Lanzar un hilo por cada cámara
threads = []
for cam_id, url in CAMERAS.items():
    t = threading.Thread(target=process_camera, args=(cam_id, url))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

cv2.destroyAllWindows()
