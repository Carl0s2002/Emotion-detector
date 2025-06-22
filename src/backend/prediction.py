from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import base64, cv2, numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from flask_socketio import SocketIO, emit




app = Flask(__name__)
CORS(app, supports_credentials=True)  
socketio = SocketIO(app,
                    cors_allowed_origins="*")



model = tf.keras.models.load_model('C:\\Users\\fdrla\\Downloads\\my_model.h5')
class_names = ["Anger", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

def preprocess_still(img_path: str) -> np.ndarray:
    """Resize to 48×48 gray, normalise to 0-1 and add batch axis."""
    img = image.load_img(img_path, color_mode="grayscale", target_size=(48, 48))
    x = image.img_to_array(img) / 255.0
    return np.expand_dims(x, axis=0)                # (1, 48, 48, 1)

def preprocess_frame(b64_jpeg: str) -> np.ndarray:
    """Decode base64 JPEG -> 48×48 gray image ready for the model."""
    jpg_original = base64.b64decode(b64_jpeg.split(",")[1])
    frame = cv2.imdecode(np.frombuffer(jpg_original, np.uint8), cv2.IMREAD_COLOR)
    frame = cv2.cvtColor(cv2.resize(frame, (48, 48)), cv2.COLOR_BGR2GRAY) / 255.0
    return frame.reshape(1, 48, 48, 1)              # (1, 48, 48, 1)

def predict(x: np.ndarray) -> dict:
    """Return {'label': str, 'conf': float}."""
    p = model.predict(x, verbose=0)[0]
    idx = int(np.argmax(p))
    return {"label": class_names[idx], "conf": float(p[idx])}

@app.route("/predict-emotion", methods=["POST"])
def predict_emotion_route():
    if "image" not in request.files or request.files["image"].filename == "":
        return jsonify({"error": "No image file provided"}), 400

    tmp_path = "temp_image.jpg"
    request.files["image"].save(tmp_path)
    result = predict(preprocess_still(tmp_path))
    return jsonify(result)

@socketio.on("frame")
def handle_frame(data: str):
    try:
        print("🔹 received frame")                    # <— prove handler ran
        result = predict(preprocess_frame(data))
        print("🔸 result", result)                   # <— now prints cleanly
        emit("prediction", result)
    except Exception as exc:
        print("⚠️ socket error:", exc)              # <— see the root cause
        emit("prediction", {"label": "error", "conf": 0.0})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
