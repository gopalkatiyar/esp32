# from flask import Flask, request, jsonify
# from PIL import Image
# import numpy as np
# import io
# import os

# app = Flask(__name__)
# SAVE_DIR = "saved_images"

# # Ensure directory exists
# os.makedirs(SAVE_DIR, exist_ok=True)

# def rgb565_to_rgb888(data, width, height):
#     """Convert RGB565 byte data to RGB888 numpy array."""
#     assert len(data) == width * height * 2, "Incorrect RGB565 data size"

#     arr = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 2))
    
#     # Convert to RGB888
#     r = ((arr[:,:,0] & 0xF8) >> 3) << 3
#     g = (((arr[:,:,0] & 0x07) << 3) | ((arr[:,:,1] & 0xE0) >> 5)) << 2
#     b = (arr[:,:,1] & 0x1F) << 3

#     rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
#     return rgb

# @app.route('/upload', methods=['POST'])
# def upload_image():
#     print(request)
#     if 'image' not in request.files:
#         print('image not in request')
#         return jsonify(success=False, message="No image part in the request"), 400

#     image_file = request.files['image']
#     if image_file.filename == '':
#         print('No selected image')
#         return jsonify(success=False, message="No selected image"), 400

#     image_bytes = image_file.read()
#     if len(image_bytes) == 0:
#         print('Empty image data')
#         return jsonify(success=False, message="Empty image data"), 400

#     try:
#         # Define resolution from ESP32-CAM (e.g., 320x240 or 160x120)
#         width, height = 320, 240  # adjust based on your ESP32-CAM settings
#         rgb_image = rgb565_to_rgb888(image_bytes, width, height)
        
#         # Convert to PIL Image and save
#         image = Image.fromarray(rgb_image, 'RGB')
#         save_path = os.path.join(SAVE_DIR, "received_image.png")
#         image.save(save_path)
#         print(f"Image saved at: {save_path}")

#         return True
#     except Exception as e:
#         print("Error:", str(e))
#         return jsonify(success=False, message="Failed to process image"), 500

# from flask import Flask, request
# import os
# from datetime import datetime

# app = Flask(__name__)

# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route('/upload', methods=['POST'])
# def upload_image():
#     try:
#         # Read the image bytes from request body
#         image_bytes = request.data

#         # Generate a unique filename using timestamp
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f'image_{timestamp}.bmp'  # You can use .jpg for JPEG format

#         # Save the image
#         with open(os.path.join(UPLOAD_FOLDER, filename), 'wb') as f:
#             f.write(image_bytes)

#         print(f"[INFO] Image saved: {filename}")
#         return "true"

#     except Exception as e:
#         print("[ERROR]", e)
#         return "false", 500




# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request
import os
from datetime import datetime
import numpy as np
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Frame size (must match ESP32-CAM config)
WIDTH = 640
HEIGHT = 480

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.data

        # Check size is valid
        expected_size = WIDTH * HEIGHT * 2  # RGB565: 2 bytes per pixel
        if len(data) != expected_size:
            print(f"[ERROR] Invalid image size: got {len(data)} bytes, expected {expected_size}")
            return f"Invalid image size: got {len(data)} bytes, expected {expected_size}", 400

        # Convert RGB565 to RGB888
        rgb_array = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        for i in range(0, len(data), 2):
            byte1 = data[i]
            byte2 = data[i + 1]
            pixel = (byte1 << 8) | byte2

            r = ((pixel >> 11) & 0x1F) << 3
            g = ((pixel >> 5) & 0x3F) << 2
            b = (pixel & 0x1F) << 3

            y = (i // 2) // WIDTH
            x = (i // 2) % WIDTH

            rgb_array[y, x] = [r, g, b]

        # Convert numpy array to image and save
        img = Image.fromarray(rgb_array, 'RGB')
        filename = f'image_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        img.save(os.path.join(UPLOAD_FOLDER, filename), 'JPEG')

        print(f"[INFO] Image saved: {filename}")
        return "true"

    except Exception as e:
        print("[ERROR]", e)
        return "false", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
