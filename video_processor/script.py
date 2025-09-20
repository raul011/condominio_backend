import os
import sys
import cv2
import onnxruntime
import onnx
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from object_detection import ObjectDetection
import tempfile
import time
import math

MODEL_FILENAME = 'model.onnx'
LABELS_FILENAME = 'labels.txt'

class FixedONNXRuntimeObjectDetection(ObjectDetection):
    """Object Detection class con dimensiones corregidas"""
    def __init__(self, model_filename, labels):
        super(FixedONNXRuntimeObjectDetection, self).__init__(labels)
        
        # Cargar y analizar el modelo
        model = onnx.load(model_filename)
        
        # Obtener dimensiones esperadas del modelo
        input_shape = model.graph.input[0].type.tensor_type.shape
        expected_dims = [dim.dim_value for dim in input_shape.dim if dim.dim_value > 0]
        
        print(f"Dimensiones originales del modelo: {[dim.dim_value if dim.dim_value > 0 else 'dynamic' for dim in input_shape.dim]}")
        
        # Si el modelo espera dimensiones específicas, usar esas
        if len(expected_dims) >= 2:
            self.expected_height = expected_dims[-2] if expected_dims[-2] > 0 else 416
            self.expected_width = expected_dims[-1] if expected_dims[-1] > 0 else 416
        else:
            # Basado en el error: el modelo espera que resulte en 13x13, pero está dando 12x22
            # Esto sugiere que necesitamos una imagen cuadrada
            self.expected_height = 416  # Típico para YOLO
            self.expected_width = 416
        
        print(f"Dimensiones que usaremos: {self.expected_width}x{self.expected_height}")
        
        with tempfile.TemporaryDirectory() as dirpath:
            temp = os.path.join(dirpath, os.path.basename(MODEL_FILENAME))
            # Hacer las dimensiones dinámicas
            model.graph.input[0].type.tensor_type.shape.dim[-1].dim_param = 'dim1'
            model.graph.input[0].type.tensor_type.shape.dim[-2].dim_param = 'dim2'
            onnx.save(model, temp)
            self.session = onnxruntime.InferenceSession(temp)
            
        self.input_name = self.session.get_inputs()[0].name
        self.is_fp16 = self.session.get_inputs()[0].type == 'tensor(float16)'
    
    def resize_image_fixed(self, image, target_width, target_height):
        """Redimensionar imagen manteniendo aspect ratio y añadiendo padding si es necesario"""
        original_width, original_height = image.size
        
        # Calcular ratio para mantener aspect ratio
        ratio = min(target_width / original_width, target_height / original_height)
        
        # Nuevas dimensiones manteniendo aspect ratio
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # Redimensionar
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crear imagen con padding (fondo negro)
        padded_image = Image.new('RGB', (target_width, target_height), (0, 0, 0))
        
        # Centrar la imagen redimensionada
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        padded_image.paste(resized_image, (x_offset, y_offset))
        
        return padded_image, (x_offset, y_offset, ratio)
    
    def predict_image(self, image):
        """Override del método predict_image para usar dimensiones fijas"""
        if isinstance(image, str):
            image = Image.open(image)
        
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        original_size = image.size
        print(f"Imagen original: {original_size}")
        
        # Redimensionar a las dimensiones exactas que espera el modelo
        processed_image, transform_info = self.resize_image_fixed(
            image, 
            self.expected_width, 
            self.expected_height
        )
        
        print(f"Imagen procesada: {processed_image.size}")
        
        # Convertir a array numpy
        img_array = np.array(processed_image, dtype=np.float32)
        
        # Llamar al método predict original
        result = self.predict(img_array)
        
        # El resultado debe ser procesado según el formato de tu modelo
        return result, original_size, transform_info
             
    def predict(self, preprocessed_image):
        """Método predict original mantenido"""
        inputs = np.array(preprocessed_image, dtype=np.float32)[np.newaxis,:,:,(2,1,0)] # RGB -> BGR
        inputs = np.ascontiguousarray(np.rollaxis(inputs, 3, 1))
        
        if self.is_fp16:
            inputs = inputs.astype(np.float16)
        
        print(f"Input shape enviado al modelo: {inputs.shape}")
        
        outputs = self.session.run(None, {self.input_name: inputs})
        
        print(f"Output shapes del modelo: {[out.shape for out in outputs]}")
        
        return np.squeeze(outputs[0]).transpose((1,2,0)).astype(np.float32)

class RealtimeDogDetectionFixed:
    def __init__(self, model_filename, labels_filename, confidence_threshold=0.5):
        # Cargar etiquetas
        if os.path.exists(labels_filename):
            with open(labels_filename, 'r') as f:
                labels = [l.strip() for l in f.readlines()]
        else:
            labels = ['perro_orinando']  # Default si no existe el archivo
        
        print(f"Etiquetas cargadas: {labels}")
        
        # Inicializar el modelo con dimensiones corregidas
        self.od_model = FixedONNXRuntimeObjectDetection(model_filename, labels)
        self.confidence_threshold = confidence_threshold
        self.labels = labels
        
        # Variables para FPS
        self.frame_count = 0
        self.start_time = time.time()
        
        print("Modelo cargado exitosamente!")
    
    def process_model_output(self, model_output, original_size, transform_info):
        """Procesar la salida del modelo con filtros ajustables"""
        predictions = []
        
        if len(model_output.shape) != 3:
            print(f"Formato de output inesperado: {model_output.shape}")
            return predictions
        
        height, width, channels = model_output.shape
        
        # Información de transformación
        x_offset, y_offset, scale_ratio = transform_info
        original_width, original_height = original_size
        
        # Encontrar todas las detecciones brutas
        raw_detections = []
        confidence_values = []
        
        for y in range(height):
            for x in range(width):
                cell_predictions = model_output[y, x, :]
                max_confidence = np.max(cell_predictions)
                max_class_idx = np.argmax(cell_predictions)
                
                confidence_values.append(max_confidence)
                
                # Usar threshold más bajo para capturar más detecciones
                if max_confidence > 0.1:  # Threshold muy bajo para debugging
                    raw_detections.append({
                        'x': x, 'y': y,
                        'confidence': max_confidence,
                        'class_idx': max_class_idx,
                        'grid_pos': (x, y)
                    })
        
        # Estadísticas de confianza para debugging
        if confidence_values:
            max_conf = np.max(confidence_values)
            min_conf = np.min(confidence_values)
            mean_conf = np.mean(confidence_values)
            threshold_matches = sum(1 for c in confidence_values if c > self.confidence_threshold)
            
            print(f"Confianzas - Max: {max_conf:.3f}, Min: {min_conf:.3f}, Media: {mean_conf:.3f}")
            print(f"Píxeles > threshold ({self.confidence_threshold:.2f}): {threshold_matches}/{len(confidence_values)}")
        
        print(f"Detecciones brutas (>0.1): {len(raw_detections)}")
        
        # Filtrar por el threshold real del usuario
        filtered_detections = [d for d in raw_detections if d['confidence'] > self.confidence_threshold]
        print(f"Después del threshold ({self.confidence_threshold:.2f}): {len(filtered_detections)}")
        
        if not filtered_detections:
            print("¡No hay detecciones que superen el threshold!")
            print("Intenta reducir el threshold con la tecla '-'")
            return predictions
        
        # Tomar más detecciones (aumentar de 10 a 20)
        filtered_detections = sorted(filtered_detections, key=lambda x: x['confidence'], reverse=True)
        top_detections = filtered_detections[:20]  # Aumentado de 10 a 20
        
        print(f"Top detecciones: {[(d['confidence'], d['grid_pos']) for d in top_detections[:5]]}")
        
        # Agrupar con threshold más permisivo
        grouped_detections = self.group_nearby_detections(top_detections, distance_threshold=2)  # Reducido de 3 a 2
        print(f"Después de agrupar: {len(grouped_detections)}")
        
        # Convertir a bounding boxes con filtros menos restrictivos
        for detection in grouped_detections:
            x, y = detection['x'], detection['y']
            confidence = detection['confidence']
            max_class_idx = detection['class_idx']
            
            # Convertir coordenadas
            cell_width = self.od_model.expected_width / width
            cell_height = self.od_model.expected_height / height
            
            center_x_processed = (x + 0.5) * cell_width
            center_y_processed = (y + 0.5) * cell_height
            
            # Hacer las cajas más grandes para capturar mejor los objetos
            box_width = cell_width * 4  # Aumentado de 3 a 4
            box_height = cell_height * 4
            
            x1_processed = center_x_processed - box_width/2
            y1_processed = center_y_processed - box_height/2
            x2_processed = center_x_processed + box_width/2
            y2_processed = center_y_processed + box_height/2
            
            # Convertir a coordenadas originales
            x1_processed -= x_offset
            y1_processed -= y_offset
            x2_processed -= x_offset  
            y2_processed -= y_offset
            
            x1_original = x1_processed / scale_ratio
            y1_original = y1_processed / scale_ratio
            x2_original = x2_processed / scale_ratio
            y2_original = y2_processed / scale_ratio
            
            # Limitar a bordes
            x1_original = max(0, min(original_width, x1_original))
            y1_original = max(0, min(original_height, y1_original))
            x2_original = max(0, min(original_width, x2_original))
            y2_original = max(0, min(original_height, y2_original))
            
            width_box = x2_original - x1_original
            height_box = y2_original - y1_original
            
            # Filtros de tamaño más permisivos
            min_box_size = min(original_width, original_height) * 0.02  # Reducido de 5% a 2%
            max_box_size = min(original_width, original_height) * 0.9   # Aumentado de 80% a 90%
            
            if width_box > 10 and height_box > 10:  # Solo verificar tamaño mínimo básico
                class_name = self.labels[max_class_idx] if max_class_idx < len(self.labels) else f"class_{max_class_idx}"
                
                predictions.append({
                    'bbox': [int(x1_original), int(y1_original), int(width_box), int(height_box)],
                    'confidence': float(confidence),
                    'class': class_name,
                    'grid_pos': (x, y),
                    'area': int(width_box * height_box)
                })
        
        print(f"Antes de NMS: {len(predictions)}")
        
        # NMS más permisivo
        predictions = self.apply_nms(predictions, iou_threshold=0.5)  # Aumentado de 0.3 a 0.5
        
        print(f"Detecciones finales: {len(predictions)}")
        if predictions:
            confidences = [f"{p['confidence']:.3f}" for p in predictions]
            print(f"Confianzas finales: {confidences}")
        
        return predictions
    
    def group_nearby_detections(self, detections, distance_threshold=3):
        """Agrupar detecciones que están muy cerca"""
        if not detections:
            return []
        
        grouped = []
        used = set()
        
        for i, det1 in enumerate(detections):
            if i in used:
                continue
            
            # Encontrar todas las detecciones cercanas
            group = [det1]
            used.add(i)
            
            for j, det2 in enumerate(detections):
                if j <= i or j in used:
                    continue
                
                # Calcular distancia Manhattan
                distance = abs(det1['x'] - det2['x']) + abs(det1['y'] - det2['y'])
                
                if distance <= distance_threshold:
                    group.append(det2)
                    used.add(j)
            
            # Tomar la detección con mayor confianza del grupo
            best_detection = max(group, key=lambda x: x['confidence'])
            grouped.append(best_detection)
        
        return grouped
    
    def apply_nms(self, predictions, iou_threshold=0.3):
        """Non-Maximum Suppression mejorado"""
        if len(predictions) <= 1:
            return predictions
        
        # Ordenar por confianza (mayor a menor)
        predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        for i, pred1 in enumerate(predictions):
            should_keep = True
            for pred2 in keep:
                iou = self.calculate_iou(pred1['bbox'], pred2['bbox'])
                if iou > iou_threshold:
                    should_keep = False
                    break
            
            if should_keep:
                keep.append(pred1)
        
        return keep
    
    def calculate_iou(self, box1, box2):
        """Calcular Intersection over Union"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Coordenadas de intersección
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right <= x_left or y_bottom <= y_top:
            return 0.0
        
        # Área de intersección
        intersection = (x_right - x_left) * (y_bottom - y_top)
        
        # Área de unión
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def draw_detections(self, image, predictions):
        """Dibujar las detecciones en la imagen"""
        if isinstance(image, np.ndarray):
            image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            image_pil = image
        
        draw = ImageDraw.Draw(image_pil)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        for pred in predictions:
            x, y, w, h = pred['bbox']
            confidence = pred['confidence']
            class_name = pred['class']
            
            # Dibujar bounding box
            color = 'red' if 'orin' in class_name.lower() else 'green'
            draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
            
            # Etiqueta con fondo
            label = f"{class_name}: {confidence:.2f}"
            bbox = draw.textbbox((x, y-25), label, font=font)
            draw.rectangle(bbox, fill=color)
            draw.text((x, y-25), label, fill='white', font=font)
        
        return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    
    def process_frame(self, frame):
        """Procesar un frame individual"""
        # Convertir frame de OpenCV a PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Usar el método predict_image corregido
        model_output, original_size, transform_info = self.od_model.predict_image(pil_image)
        
        # Procesar la salida del modelo
        predictions = self.process_model_output(model_output, original_size, transform_info)
        
        # Dibujar detecciones
        result_frame = self.draw_detections(frame.copy(), predictions)
        
        return result_frame, len(predictions), predictions
    
    def run_camera(self, camera_source=0):
        """Ejecutar detección en tiempo real"""
        if isinstance(camera_source, str):
            print(f"Conectando a: {camera_source}")
            cap = cv2.VideoCapture(camera_source)
        else:
            print(f"Usando cámara local: {camera_source}")
            cap = cv2.VideoCapture(camera_source)
        
        if not cap.isOpened():
            print(f"Error: No se pudo abrir la cámara {camera_source}")
            return
        
        # Configurar resolución si es cámara local
        if isinstance(camera_source, int):
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Controles:")
        print("  'q': Salir")
        print("  's': Screenshot")  
        print("  '+': Aumentar threshold")
        print("  '-': Disminuir threshold")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: No se pudo leer el frame")
                break
            
            # Procesar frame
            start_time = time.time()
            result_frame, detection_count, predictions = self.process_frame(frame)
            process_time = time.time() - start_time
            
            # Calcular FPS
            self.frame_count += 1
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            
            # Información extendida en pantalla
            info_y = 30
            info_texts = [
                f"FPS: {fps:.1f}",
                f"Tiempo: {process_time*1000:.0f}ms",
                f"Threshold: {self.confidence_threshold:.2f}",
                f"Detecciones: {detection_count}"
            ]
            
            for text in info_texts:
                cv2.putText(result_frame, text, (10, info_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                info_y += 25
            
            # Mostrar información detallada de detecciones
            if detection_count > 0:
                cv2.putText(result_frame, "DETECCIONES ENCONTRADAS:", (10, info_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                info_y += 20
                
                for i, pred in enumerate(predictions[:5]):  # Mostrar hasta 5 detecciones
                    detail_text = f"  {i+1}. {pred['class']}: {pred['confidence']:.3f}"
                    cv2.putText(result_frame, detail_text, (10, info_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                    info_y += 18
            else:
                # Mensaje de ayuda cuando no hay detecciones
                help_texts = [
                    "Sin detecciones. Prueba:",
                    "- Tecla '-' para bajar threshold",
                    "- Mejora iluminacion",  
                    "- Acerca camara al perro"
                ]
                for help_text in help_texts:
                    cv2.putText(result_frame, help_text, (10, info_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                    info_y += 18
            
            # Mensaje de detección
            if detection_count > 0:
                cv2.putText(result_frame, "PERRO ORINANDO DETECTADO!", 
                           (10, result_frame.shape[0] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            cv2.imshow('Detector Perro Orinando - CORREGIDO', result_frame)
            
            # Controles de teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"detection_{int(time.time())}.jpg"
                cv2.imwrite(filename, result_frame)
                print(f"Screenshot guardado: {filename}")
            elif key == ord('+') or key == ord('='):
                self.confidence_threshold = min(1.0, self.confidence_threshold + 0.05)
                print(f"Threshold: {self.confidence_threshold:.2f}")
            elif key == ord('-'):
                self.confidence_threshold = max(0.0, self.confidence_threshold - 0.05)
                print(f"Threshold: {self.confidence_threshold:.2f}")
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    print("=== Detector de Perros Orinando - VERSIÓN CORREGIDA ===")
    print("Esta versión maneja correctamente las dimensiones del modelo")
    print()
    
    if not os.path.exists(MODEL_FILENAME):
        print(f"Error: No se encuentra {MODEL_FILENAME}")
        return
    
    try:
        # Threshold muy alto para evitar falsos positivos
        detector = RealtimeDogDetectionFixed(
            MODEL_FILENAME, 
            LABELS_FILENAME, 
            confidence_threshold=0.95  # Threshold muy alto
        )
    except Exception as e:
        print(f"Error inicializando detector: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if len(sys.argv) > 1:
        camera_source = sys.argv[1]
        if camera_source.isdigit():
            camera_source = int(camera_source)
        detector.run_camera(camera_source)
    else:
        print("Para DroidCam: python script.py http://IP_CELULAR:4747/video")
        detector.run_camera(0)

if __name__ == '__main__':
    main()