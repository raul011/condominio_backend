import onnxruntime
import numpy as np
from PIL import Image, ImageDraw
import os

# === Configuración ===
MODEL_FILENAME = "model.onnx"
IMAGE_FILENAME = "test.jpeg"  # usa cualquier imagen

# Anchors Tiny YOLOv2 (Custom Vision suele exportar estos)
ANCHORS = [
    (1.08, 1.19),
    (3.42, 4.41),
    (6.63, 11.38)
]
GRID_SIZE = 13
NUM_ANCHORS = 3
NUM_CLASSES = 1  # solo 1 clase en tu modelo

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

NUM_ANCHORS = 5
NUM_CLASSES = 1
GRID_SIZE = 13

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def process_model_output(output, conf_threshold=0.3):
    """
    Decodifica salida Tiny YOLOv2 con 5 anchors y 1 clase.
    """
    output = output[0]  # (30, 13, 13)
    output = output.reshape((NUM_ANCHORS, 5 + NUM_CLASSES, GRID_SIZE, GRID_SIZE))
    detections = []

    for a in range(NUM_ANCHORS):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                tx, ty, tw, th, tc = output[a, 0:5, i, j]
                class_probs = output[a, 5:, i, j]

                bx = (sigmoid(tx) + j) / GRID_SIZE
                by = (sigmoid(ty) + i) / GRID_SIZE
                bw = (np.exp(tw) * ANCHORS[a][0]) / GRID_SIZE
                bh = (np.exp(th) * ANCHORS[a][1]) / GRID_SIZE
                conf = sigmoid(tc)

                # Como tienes 1 clase, no hace falta softmax
                score = conf * sigmoid(class_probs[0])
                class_id = 0

                if score > conf_threshold:
                    x1 = bx - bw/2
                    y1 = by - bh/2
                    x2 = bx + bw/2
                    y2 = by + bh/2
                    detections.append([x1, y1, x2, y2, float(score), class_id])

    return detections



def main():
    if not os.path.exists(MODEL_FILENAME):
        print(f"❌ No se encontró el modelo: {MODEL_FILENAME}")
        return
    if not os.path.exists(IMAGE_FILENAME):
        print(f"❌ No se encontró la imagen: {IMAGE_FILENAME}")
        return

    # === Cargar modelo ===
    session = onnxruntime.InferenceSession(MODEL_FILENAME)
    input_name = session.get_inputs()[0].name

    # === Preparar imagen ===
    img = Image.open(IMAGE_FILENAME).convert("RGB")
    original_w, original_h = img.size
    resized = img.resize((416, 416))
    img_array = np.array(resized, dtype=np.float32).transpose(2, 0, 1)
    img_array = np.expand_dims(img_array, axis=0)

    # === Inferencia ===
    outputs = session.run(None, {input_name: img_array})
    detections = process_model_output(outputs[0], conf_threshold=0.3)

    print("➡️ Detecciones encontradas:")
    for det in detections:
        print(det)

    # === Dibujar cajas ===
    draw = ImageDraw.Draw(img)
    for (x1, y1, x2, y2, score, class_id) in detections:
        # Escalar a tamaño original
        x1 = int(x1 * original_w)
        y1 = int(y1 * original_h)
        x2 = int(x2 * original_w)
        y2 = int(y2 * original_h)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        draw.text((x1, y1), f"{score:.2f}", fill="red")

    img.save("result.jpg")
    print("✅ Resultado guardado en result.jpg")


if __name__ == "__main__":
    main()
