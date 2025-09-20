import onnxruntime
import onnx
import numpy as np
from PIL import Image
import os

MODEL_FILENAME = "model.onnx"
IMAGE_FILENAME = "test.jpeg"  # usa cualquier imagen, aunque no tenga perro


def main():
    if not os.path.exists(MODEL_FILENAME):
        print(f"❌ No se encontró el modelo: {MODEL_FILENAME}")
        return
    if not os.path.exists(IMAGE_FILENAME):
        print(f"❌ No se encontró la imagen: {IMAGE_FILENAME}")
        return

    # Cargar modelo con onnxruntime
    session = onnxruntime.InferenceSession(MODEL_FILENAME)
    input_name = session.get_inputs()[0].name
    input_shape = session.get_inputs()[0].shape
    print(f"➡️ Nombre de entrada: {input_name}")
    print(f"➡️ Forma de entrada declarada: {input_shape}")

    # Preparar imagen
    img = Image.open(IMAGE_FILENAME).convert("RGB")
    img = img.resize((416, 416))  # tamaño típico YOLO, ajusta si tu modelo es distinto
    img_array = np.array(img, dtype=np.float32)
    img_array = img_array.transpose(2, 0, 1)  # HWC -> CHW
    img_array = np.expand_dims(img_array, axis=0)  # NCHW
    print(f"➡️ Shape de la imagen enviada: {img_array.shape}")

    # Ejecutar inferencia
    outputs = session.run(None, {input_name: img_array})
    print("➡️ Output shapes del modelo:")
    for i, out in enumerate(outputs):
        print(f"   Salida {i}: {out.shape}")


if __name__ == "__main__":
    main()
