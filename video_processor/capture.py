import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image
from object_detection import ObjectDetection  # archivo exportado junto al modelo

# ===================== CONFIGURACIÓN =====================
CAMERA_URL = "http://192.168.0.94:4747/video"  # cambia a tu IP
MODEL_PATH = "video_processor/model.onnx"
LABELS_PATH = "video_processor/labels.txt"
PROB_THRESHOLD = 0.2  # umbral de confianza
INPUT_SIZE = (416, 416)  # tamaño esperado por el modelo
# ===========================================================

# Cargar etiquetas
with open(LABELS_PATH) as f:
    labels = [line.strip() for line in f.readlines()]

# Inicializar sesión ONNX
session = ort.InferenceSession(MODEL_PATH)
input_name = session.get_inputs()[0].name
print("Modelo espera:", session.get_inputs()[0].shape)

# Subclase que conecta ObjectDetection con onnxruntime
class OnnxObjectDetection(ObjectDetection):
    def __init__(self, labels, session, input_name, prob_threshold=0.2, input_size=(416,416)):
        super().__init__(labels, prob_threshold=prob_threshold)
        self.session = session
        self.input_name = input_name
        self.input_size = input_size

    def predict(self, preprocessed_inputs):
        # 🔒 Forzar resize al tamaño esperado por el modelo
        preprocessed_inputs = preprocessed_inputs.resize(self.input_size)

        img_data = np.array(preprocessed_inputs, dtype=np.float32) / 255.0
        img_data = np.expand_dims(img_data, axis=0)  # (1,H,W,3)
        img_data = np.transpose(img_data, (0, 3, 1, 2))  # (1,3,H,W)
        outputs = self.session.run(None, {self.input_name: img_data})
        return np.squeeze(outputs[0]).transpose((1, 2, 0))

# Inicializar detector
detector = OnnxObjectDetection(labels, session, input_name, prob_threshold=PROB_THRESHOLD, input_size=INPUT_SIZE)

# Abrir cámara
cap = cv2.VideoCapture(CAMERA_URL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo leer frame")
        break

    # OpenCV → PIL
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Predicciones
    predictions = detector.predict_image(pil_img)

    for pred in predictions:
        tag = pred["tagName"]
        prob = pred["probability"]
        bb = pred["boundingBox"]

        # Convertir coords relativas a pixeles
        h, w, _ = frame.shape
        x1 = int(bb["left"] * w)
        y1 = int(bb["top"] * h)
        x2 = int((bb["left"] + bb["width"]) * w)
        y2 = int((bb["top"] + bb["height"]) * h)

        # Dibujar
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, f"{tag}: {prob:.2f}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        if tag.lower() == "perro orinando":
            print(f"🚨 Detectado: {tag} ({prob:.2f})")

    cv2.imshow("Camara Celular", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()