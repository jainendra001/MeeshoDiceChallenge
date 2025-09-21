from flask import Flask, request, jsonify
from PIL import Image
import io
import numpy as np
import tensorflow as tf

app = Flask(__name__)

# Load pre-trained EfficientNet-B0 model (or a similar lightweight CNN)
# For a real application, you would fine-tune this on your specific dataset.
# Here, we'll use a pre-trained model for demonstration and mock the quality assessment.
try:
    model = tf.keras.applications.EfficientNetB0(weights='imagenet')
except Exception as e:
    print(f"Could not load EfficientNetB0 weights: {e}")
    print("Proceeding with a dummy model for demonstration.")
    # Create a dummy model if EfficientNetB0 fails to load (e.g., no internet)
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(1000, activation='softmax')
    ])

@app.route('/api/v1/image/analyze', methods=['POST'])
def analyze_image():
    if 'image_url' not in request.json:
        return jsonify({"error": "image_url is required"}), 400

    image_url = request.json['image_url']
    
    # In a real scenario, you would download the image from the URL
    # and perform actual analysis. For this demonstration, we'll mock the results.
    print(f"Analyzing image from URL: {image_url}")

    # Mock analysis results
    # These scores would typically come from your fine-tuned model
    blurriness_score = np.random.uniform(0.0, 1.0)
    is_stock_photo = np.random.uniform(0.0, 1.0)

    # Simulate some basic image processing if a real model was loaded
    if 'EfficientNetB0' in str(type(model)): # Check if it's the real model
        try:
            # Dummy image processing for demonstration
            # In a real app, you'd fetch the image from image_url
            # and preprocess it for the model.
            dummy_image = Image.new('RGB', (224, 224), color = 'red')
            img_array = tf.keras.preprocessing.image.img_to_array(dummy_image)
            img_array = tf.expand_dims(img_array, 0) # Create a batch
            img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
            
            # Perform a dummy prediction to simulate model usage
            _ = model.predict(img_array)
            print("Dummy model prediction performed.")
        except Exception as e:
            print(f"Error during dummy model prediction: {e}")

    return jsonify({
        "blurriness_score": float(blurriness_score),
        "is_stock_photo": float(is_stock_photo)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
