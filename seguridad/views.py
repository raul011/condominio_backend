from django.shortcuts import render
from rest_framework import viewsets
from .models import RegistroSeguridad, Reclamo
from .serializers import RegistroSeguridadSerializer, ReclamoSerializer

# Imports for Object Detection
import onnxruntime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import io
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from .object_detection import ObjectDetection # Using the provided library file

class RegistroSeguridadViewSet(viewsets.ModelViewSet):
    queryset = RegistroSeguridad.objects.all()
    serializer_class = RegistroSeguridadSerializer

class ReclamoViewSet(viewsets.ModelViewSet):
    queryset = Reclamo.objects.all()
    serializer_class = ReclamoSerializer

# --- Object Detection Logic ---

# Define paths relative to BASE_DIR
MODEL_FILENAME = os.path.join(settings.BASE_DIR, 'video_processor', 'model.onnx')
LABELS_FILENAME = os.path.join(settings.BASE_DIR, 'video_processor', 'labels.txt')

class ONNXObjectDetection(ObjectDetection):
    """
    This class is a faithful port of the logic from the user's original
    detect.py and object_detection.py scripts.
    """
    def __init__(self, labels, prob_threshold=0.3, max_detections=20):
        super().__init__(labels, prob_threshold, max_detections)
        self.session = onnxruntime.InferenceSession(MODEL_FILENAME)
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = (416, 416)

    def preprocess(self, image):
        """
        Performs a direct, distorting resize to 416x416, as done in the
        original object_detection.py script.
        """
        image = image.convert("RGB") if image.mode != "RGB" else image
        image = self._update_orientation(image) # From base class
        image = image.resize(self.input_shape, Image.Resampling.LANCZOS)
        return image

    def predict(self, preprocessed_inputs):
        """
        Converts the image to a numpy array without normalization and without
        swapping color channels, as done in the original detect.py script.
        """
        img_array = np.array(preprocessed_inputs, dtype=np.float32)
        
        # Reshape for the model: (H, W, C) -> (1, C, H, W)
        img_array = np.expand_dims(img_array, axis=0)  # (1, H, W, C)
        img_array = np.transpose(img_array, (0, 3, 1, 2))  # (1, C, H, W)

        outputs = self.session.run(None, {self.input_name: img_array})
        
        # Transpose output back to the format expected by postprocess: (H, W, C)
        output = outputs[0][0]  # (C, H, W)
        output = np.transpose(output, (1, 2, 0))  # (H, W, C)
        return output

class ObjectDetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if 'image' not in request.data:
            return Response({"error": "No image provided"}, status=400)

        image_file = request.data['image']

        try:
            with open(LABELS_FILENAME) as f:
                labels = [line.strip() for line in f.readlines()]
            
            # Using a more balanced threshold to reduce false positives
            detector = ONNXObjectDetection(labels, prob_threshold=0.6)

            image = Image.open(image_file)
            original_image = image.copy().convert("RGB")
            
            # The predict_image method from the base class will orchestrate
            # the new preprocess -> predict -> postprocess flow
            predictions = detector.predict_image(image)

            draw = ImageDraw.Draw(original_image)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default()
            
            if predictions:
                for r in predictions:
                    box = r["boundingBox"]
                    left = int(box["left"] * original_image.width)
                    top = int(box["top"] * original_image.height)
                    right = int((box["left"] + box["width"]) * original_image.width)
                    bottom = int((box["top"] + box["height"]) * original_image.height)
                    
                    draw.rectangle([left, top, right, bottom], outline="red", width=3)
                    
                    text = f"{r['tagName']} {r['probability']:.2f}"
                    text_bbox = draw.textbbox((left, top - 25 if top > 25 else top), text, font=font)
                    draw.rectangle(text_bbox, fill="red")
                    draw.text((left, top - 25 if top > 25 else top), text, fill="white", font=font)
            else:
                msg = "No se encontraron detecciones"
                text_bbox = draw.textbbox((0, 0), msg, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = (original_image.width - text_width) / 2
                text_y = (original_image.height - text_height) / 2
                draw.rectangle(
                    [text_x - 10, text_y - 10, text_x + text_width + 10, text_y + text_height + 10],
                    fill=(0, 0, 0, 128)
                )
                draw.text((text_x, text_y), msg, font=font, fill="white")

            img_byte_arr = io.BytesIO()
            original_image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)

            return HttpResponse(img_byte_arr, content_type='image/jpeg')

        except Exception as e:
            # Return a more detailed error message for debugging
            import traceback
            return Response({
                "error": "An internal error occurred.",
                "details": str(e),
                "trace": traceback.format_exc()
            }, status=500)
