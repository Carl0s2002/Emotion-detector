from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image




app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication


# # Load your pre-trained emotion recognition model (ensure it's the correct path)
model = tf.keras.models.load_model('C:\\Users\\fdrla\\Downloads\\my_model.h5')
model.summary() 
def preprocess_image(img_path: str):
    """
    Preprocess the image to match the input format of the model:
    - Resize to 48x48
    - Convert to grayscale
    - Normalize pixel values
    - Add batch dimension
    """
    # Load the image with grayscale=True and resize to 48x48
    img = image.load_img(img_path, color_mode='grayscale', target_size=(48, 48))
    
    # Convert the image to an array
    x = image.img_to_array(img)
    
    # Add batch dimension (this makes it (1, 48, 48, 1))
    x = np.expand_dims(x, axis=0)
    
    # Normalize pixel values to [0, 1]
    x /= 255
    
    return x

def predict_emotion(image_path: str):
    """
    Function to predict the emotion from the image using the pre-trained model.
    """
    # Preprocess the image
    img_expanded = preprocess_image(image_path)

    # Get predictions
    predictions = model.predict(img_expanded)

    # Get the class with the highest probability (assuming it's a multi-class classification)
    predicted_class = np.argmax(predictions, axis=1)

    # Map the class index to an emotion label (modify according to your model's output classes)
    emotion_labels = ["Anger", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
    predicted_emotion = emotion_labels[predicted_class[0]]

    return predicted_emotion

@app.route("/predict-emotion", methods=["POST"])
def predict_emotion_route():
    # Check if an image is provided
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    image = request.files["image"]  # Get the image file from the request
    
    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the uploaded image to a temporary file
        temp_image_path = 'temp_image.jpg'
        image.save(temp_image_path)

        # Call the emotion prediction function
        emotion = predict_emotion(temp_image_path)

        return jsonify({"emotion": emotion})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
