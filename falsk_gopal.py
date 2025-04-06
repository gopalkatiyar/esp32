from flask import Flask, request, jsonify, render_template_string, render_template
import face_recognition
import cv2
import os
import pickle
import numpy as np
import tempfile

app = Flask(__name__)

# Directory and file for storing known faces and their encodings
KNOWN_FACES_DIR = 'known_faces'
ENCODING_FILE = 'encodings.pickle'

def add_face_to_database(image_path, name):
    """
    Adds a face to the database by loading the image, extracting its encoding,
    appending it to the pickle file, and saving a copy of the image to disk.
    """
    print("Processing add_face_to_database for", name)
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=1, model='hog')
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    if not face_encodings:
        print("[❌] No face found in image for", name)
        return False  # Indicate that no face was found

    encoding = face_encodings[0]

    # Load existing encodings or initialize a new dictionary
    if os.path.exists(ENCODING_FILE):
        with open(ENCODING_FILE, 'rb') as f:
            encoding_data = pickle.load(f)
    else:
        encoding_data = {'encodings': [], 'names': []}

    encoding_data['encodings'].append(encoding)
    encoding_data['names'].append(name)

    # Save updated encodings to disk
    with open(ENCODING_FILE, 'wb') as f:
        pickle.dump(encoding_data, f)

    # Save the image for future reference
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    save_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(save_path, bgr)

    print(f"[✅] Face for {name} added successfully.")
    return True

def recognize_face_from_image(image_path, tolerance=0.5):
    """
    Compares faces in the provided image against stored face encodings.
    Returns True if a match is found; otherwise, returns False.
    """
    if not os.path.exists(ENCODING_FILE):
        print("[❌] No database found. Add some faces first.")
        return False

    with open(ENCODING_FILE, 'rb') as f:
        data = pickle.load(f)

    input_image = face_recognition.load_image_file(image_path)
    input_locations = face_recognition.face_locations(input_image, number_of_times_to_upsample=2, model='hog')
    input_encodings = face_recognition.face_encodings(input_image, input_locations)

    if not input_encodings:
        print("[❌] No face found in input image.")
        return False

    # Check each face found in the image for a match
    for face_encoding in input_encodings:
        matches = face_recognition.compare_faces(data['encodings'], face_encoding, tolerance=tolerance)
        if any(matches):
            print("[✅] At least one matching face found!")
            return True

    print("[❌] No match found in the image.")
    return False

# --------------------------
# Route 1: HTML page for adding a face to the database
# --------------------------
@app.route('/add_face', methods=['GET', 'POST'])
def add_face():
    if request.method == 'POST':
        name = request.form.get('name')
        file = request.files.get('image')

        if not file or not name or name.strip() == "":
            return "Name and image file are required.", 400

        # Save the uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        file.save(temp_file.name)
        temp_file.close()

        success = add_face_to_database(temp_file.name, name)

        # Remove the temporary file after processing
        os.remove(temp_file.name)

        if success:
            return f"Face for {name} added successfully."
        else:
            return "No detectable face found in the uploaded image.", 400

    # For a GET request, render a simple HTML upload form
    return render_template('add_user.html')

# --------------------------
# Route 2: Endpoint for ESP32 Cam to send an image for face recognition
# --------------------------
@app.route('/recognize', methods=['POST'])
def recognize():
    file = request.files.get('image')
    if not file:
        return jsonify({"result": False, "error": "No image provided"}), 400

    # Save the incoming image to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    file.save(temp_file.name)
    temp_file.close()

    match_found = recognize_face_from_image(temp_file.name)

    # Remove the temporary file after processing
    os.remove(temp_file.name)

    return jsonify({"result": match_found})

if __name__ == '__main__':
    # Running on all interfaces so that the ESP32 Cam can reach this endpoint
    app.run(host='0.0.0.0', port=5000, debug=True)
