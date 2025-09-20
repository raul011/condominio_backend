import cv2
import threading
from PIL import Image
from onnxruntime_predict import ONNXRuntimeObjectDetection

MODEL_FILENAME = "model.onnx"
LABELS_FILENAME = "labels.txt"

# Cargar etiquetas
with open(LABELS_FILENAME, "r", encoding="utf-8") as f:
    labels = [l.strip() for l in f.readlines()]

# Cargar modelo
od_model = ONNXRuntimeObjectDetection(MODEL_FILENAME, labels)

# Lista de cámaras (pueden ser DroidCam, RTSP o locales)
CAMERAS = {
    "CAM1": "http://192.168.0.94:4747/video",
    "CAM2": "http://192.168.0.175:4747/video"
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

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{tag_name} {prob:.2f}",
                            (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2)

        except Exception as e:
            print(f"Error en {cam_id}: {e}")

        # Ventana con nombre de la cámara
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

# Esperar que todos terminen
for t in threads:
    t.join()

cv2.destroyAllWindows()
