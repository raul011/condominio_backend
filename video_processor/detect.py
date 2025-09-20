import onnxruntime
import numpy as np
from PIL import Image, ImageDraw
from object_detection import ObjectDetection  # el archivo que bajaste
import os

MODEL_FILENAME = "model.onnx"
LABELS_FILENAME = "labels.txt"
IMAGE_FILENAME = "test.jpeg"

class ONNXObjectDetection(ObjectDetection):
    def __init__(self, labels, prob_threshold=0.3, max_detections=20):
        super().__init__(labels, prob_threshold, max_detections)
        self.session = onnxruntime.InferenceSession(MODEL_FILENAME)
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, preprocessed_inputs):
        """
        Corre el modelo ONNX y devuelve el output (H, W, C).
        """
        img_array = np.array(preprocessed_inputs, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)  # (1, H, W, C)
        img_array = np.transpose(img_array, (0, 3, 1, 2))  # (1, C, H, W)

        outputs = self.session.run(None, {self.input_name: img_array})
        output = outputs[0][0]  # (C, H, W)
        output = np.transpose(output, (1, 2, 0))  # (H, W, C)
        return output


def main():
    # Verificar archivos
    if not os.path.exists(MODEL_FILENAME):
        print(f"❌ No se encontró el modelo {MODEL_FILENAME}")
        return
    if not os.path.exists(LABELS_FILENAME):
        print(f"❌ No se encontró {LABELS_FILENAME}")
        return
    if not os.path.exists(IMAGE_FILENAME):
        print(f"❌ No se encontró {IMAGE_FILENAME}")
        return

    # Cargar labels
    with open(LABELS_FILENAME) as f:
        labels = [line.strip() for line in f.readlines()]

    # Inicializar detector
    detector = ONNXObjectDetection(labels, prob_threshold=0.3)

    # Abrir imagen
    image = Image.open(IMAGE_FILENAME)
    results = detector.predict_image(image)

    print("➡️ Resultados:")
    for r in results:
        print(r)

    # Dibujar cajas
    draw = ImageDraw.Draw(image)
    for r in results:
        box = r["boundingBox"]
        left = int(box["left"] * image.width)
        top = int(box["top"] * image.height)
        right = int((box["left"] + box["width"]) * image.width)
        bottom = int((box["top"] + box["height"]) * image.height)
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        draw.text((left, top), f"{r['tagName']} {r['probability']:.2f}", fill="red")

    image.save("result.jpg")
    print("✅ Resultado guardado en result.jpg")


if __name__ == "__main__":
    main()
