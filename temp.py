from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import io
import os

app = Flask(__name__)
SAVE_DIR = "saved_images"

# Ensure directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

def rgb565_to_rgb888(data, width, height):
    """Convert RGB565 byte data to RGB888 numpy array."""
    assert len(data) == width * height * 2, "Incorrect RGB565 data size"

    arr = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 2))
    
    # Convert to RGB888
    r = ((arr[:,:,0] & 0xF8) >> 3) << 3
    g = (((arr[:,:,0] & 0x07) << 3) | ((arr[:,:,1] & 0xE0) >> 5)) << 2
    b = (arr[:,:,1] & 0x1F) << 3

    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return rgb

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify(success=False, message="No image part in the request"), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify(success=False, message="No selected image"), 400

    image_bytes = image_file.read()
    if len(image_bytes) == 0:
        return jsonify(success=False, message="Empty image data"), 400

    try:
        # Define resolution from ESP32-CAM (e.g., 320x240 or 160x120)
        width, height = 320, 240  # adjust based on your ESP32-CAM settings
        rgb_image = rgb565_to_rgb888(image_bytes, width, height)
        
        # Convert to PIL Image and save
        image = Image.fromarray(rgb_image, 'RGB')
        save_path = os.path.join(SAVE_DIR, "received_image.png")
        image.save(save_path)
        print(f"Image saved at: {save_path}")

        return jsonify(success=True, message="Image received and saved")
    except Exception as e:
        print("Error:", str(e))
        return jsonify(success=False, message="Failed to process image"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
