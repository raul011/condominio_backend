import cv2
import threading
import numpy as np
from PIL import Image
from shapely.geometry import Point, Polygon  # pip install shapely
from onnxruntime_predict import ONNXRuntimeObjectDetection

MODEL_FILENAME = "model.onnx"
LABELS_FILENAME = "labels.txt"

# Cargar etiquetas
with open(LABELS_FILENAME, "r", encoding="utf-8") as f:
    labels = [l.strip() for l in f.readlines()]

# Cargar modelo
od_model = ONNXRuntimeObjectDetection(MODEL_FILENAME, labels)

# Lista de cámaras
CAMERAS = {
    "CAM1": "http://192.168.0.94:4747/video",
    "CAM2": "http://192.168.0.175:4747/video"
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
