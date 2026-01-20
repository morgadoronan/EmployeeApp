import cv2
import numpy as np
import tensorflow as tf
import time
from PIL import Image, ImageOps

model = tf.keras.layers.TFSMLayer("model_saved", call_endpoint='serve')

with open("labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# start video capture
# cap = cv2.VideoCapture(0)  # Para câmera
cap = cv2.VideoCapture("C:\\Users\\r.morgado\\Downloads\\WhatsApp Video 2025-12-15 at 16.15.42.mp4")

if not cap.isOpened():
    print("error: camera not found")
    exit()

print("Starting Monitoring...")

# Settings
IMG_SIZE = 224
ANOMALY_LABEL = "NOK"
THRESHOLD = 0.50
while True:
    ret, frame = cap.read()
    if not ret:
        print("Fail to grab frame")
        break

    image = Image.fromarray(frame).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Prediction
    prediction = model(data).numpy()
    index = np.argmax(prediction)
    class_name = labels[index]
    confidence_score = prediction[0][index]

    # clean class name
    class_name_clean = class_name[2:].strip()

    # Logging
    print(f"Detected: {class_name_clean} | Confidence: {confidence_score:.2f} | Confidence: OK={prediction[0][0]:.2f}, NOK={prediction[0][1]:.2f}")

    # Detect anomaly
    if class_name_clean == ANOMALY_LABEL and confidence_score >= THRESHOLD:
        print("🚨 ALERT: ANOMALY!")
        print("-----------------------------------------")

    # Delay for next frame
    time.sleep(0.5)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Monitoring finished.")