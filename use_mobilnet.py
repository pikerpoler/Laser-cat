import cv2
import numpy as np
import tensorflow.lite as tflite

# Load the model
interpreter = tflite.Interpreter(model_path="~/models/detect.tflite")
interpreter.allocate_tensors()

# Load labels
LABELS = {17: "cat"}  # COCO dataset ID for 'cat'

# Load image
image = cv2.imread("/home/pi/image.jpg")
input_shape = interpreter.get_input_details()[0]["shape"]
input_data = cv2.resize(image, (300, 300))
input_data = np.expand_dims(input_data, axis=0).astype(np.uint8)

# Run inference
interpreter.set_tensor(interpreter.get_input_details()[0]["index"], input_data)
interpreter.invoke()

# Get output
boxes = interpreter.get_tensor(interpreter.get_output_details()[0]["index"])[0]
classes = interpreter.get_tensor(interpreter.get_output_details()[1]["index"])[0]
scores = interpreter.get_tensor(interpreter.get_output_details()[2]["index"])[0]

# Draw bounding box for detected cat
for i in range(len(scores)):
    if scores[i] > 0.5 and int(classes[i]) == 17:  # 17 = "cat"
        y1, x1, y2, x2 = boxes[i]
        h, w, _ = image.shape
        x1, y1, x2, y2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            image, "Cat", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
        )

# Save output
cv2.imwrite("/home/pi/cat_detected.jpg", image)
