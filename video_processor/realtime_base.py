import cv2
from PIL import Image
from onnxruntime_predict import ONNXRuntimeObjectDetection

MODEL_FILENAME = "model.onnx"
LABELS_FILENAME = "labels.txt"

# Cargar etiquetas
with open(LABELS_FILENAME, "r", encoding="utf-8") as f:
    labels = [l.strip() for l in f.readlines()]

# Cargar el modelo
od_model = ONNXRuntimeObjectDetection(MODEL_FILENAME, labels)

# 👉 Usa la URL de DroidCam (ajusta la IP/puerto según tu celular)
CAMERA_URL = "http://192.168.0.94:4747/video"  # ⚠️ reemplaza con la IP real de tu DroidCam
#CAMERA_URL = "http://192.168.0.175:4747/video"  # ⚠️ reemplaza con la IP real de tu DroidCam


cap = cv2.VideoCapture(CAMERA_URL)

if not cap.isOpened():
    print(f"❌ No se pudo abrir la cámara en {CAMERA_URL}")
    exit()

print("✅ Cámara abierta. Presiona 'q' para salir.")

def is_numeric(value):
    """Check if a value can be converted to float"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def parse_prediction(pred, frame_width, frame_height):
    """Parse prediction from your specific model format"""
    try:
        # Handle your specific dictionary format
        if isinstance(pred, dict):
            if 'boundingBox' in pred and 'probability' in pred:
                bbox = pred['boundingBox']
                prob = pred['probability']
                tag_id = pred.get('tagId', 0)
                tag_name = pred.get('tagName', 'unknown')
                
                # Extract normalized coordinates (0.0 to 1.0)
                left = bbox['left']
                top = bbox['top']
                width = bbox['width']
                height = bbox['height']
                
                # Convert to pixel coordinates
                x1 = int(left * frame_width)
                y1 = int(top * frame_height)
                x2 = int((left + width) * frame_width)
                y2 = int((top + height) * frame_height)
                
                # Clamp coordinates to frame bounds
                x1 = max(0, min(x1, frame_width))
                y1 = max(0, min(y1, frame_height))
                x2 = max(0, min(x2, frame_width))
                y2 = max(0, min(y2, frame_height))
                
                return x1, y1, x2, y2, float(prob), int(tag_id), tag_name
        
        return None
        
    except Exception as e:
        print(f"Error parsing prediction: {e}")
        return None

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ No se recibió frame, revisa la conexión DroidCam.")
        break

    # Convertir BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convertir numpy → PIL
    pil_image = Image.fromarray(rgb_frame)

    try:
        # Ejecutar predicción
        predictions = od_model.predict_image(pil_image)
        
        # Get frame dimensions
        frame_height, frame_width = frame.shape[:2]
        
        # Debug: Print predictions format only for first few frames
        if frame_count < 3:
            print(f"Frame {frame_count} - Predictions type: {type(predictions)}")
            if predictions:
                print(f"First prediction: {predictions[0] if predictions else 'Empty'}")
            frame_count += 1

        # Dibujar resultados
        for pred in predictions:
            parsed = parse_prediction(pred, frame_width, frame_height)
            if parsed is None:
                continue
                
            x1, y1, x2, y2, prob, tag_id, tag_name = parsed
            
            # Validar coordenadas
            if x1 >= x2 or y1 >= y2:
                continue
            
            # Filter by confidence threshold
            if prob < 0.6:  # Only show detections with >30% confidence
                continue

            # Dibujar bounding box y etiqueta
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{tag_name} {prob:.2f}",
                        (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

    except Exception as e:
        print(f"Error durante la predicción: {e}")
        continue

    cv2.imshow("Detección en tiempo real", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()