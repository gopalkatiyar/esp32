import face_recognition
import cv2
import os
import pickle
import numpy as np

KNOWN_FACES_DIR = 'known_faces'
ENCODING_FILE = 'encodings.pickle'
print(1)

def add_face_to_database(image_path, name):
    """
    Adds face to database and saves encoding.
    """
    print(1)
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=1, model='hog')
    face_encodings = face_recognition.face_encodings(image, face_locations)
    print('done adding')
    if not face_encodings:
        print("[❌] No face found.")
        return

    encoding = face_encodings[0]

    # Load or initialize encodings
    if os.path.exists(ENCODING_FILE):
        with open(ENCODING_FILE, 'rb') as f:
            encoding_data = pickle.load(f)
    else:
        encoding_data = {'encodings': [], 'names': []}

    encoding_data['encodings'].append(encoding)
    encoding_data['names'].append(name)

    # Save the updated encodings
    with open(ENCODING_FILE, 'wb') as f:
        pickle.dump(encoding_data, f)

    # Save image for reference
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    save_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(save_path, bgr)

    print(f"[✅] Face for {name} added.")


def recognize_face(input_image_path, tolerance=0.5):
    """
    Recognizes face from input image against saved encodings.
    """
    if not os.path.exists(ENCODING_FILE):
        print("[❌] No database found. Add some faces first.")
        return

    with open(ENCODING_FILE, 'rb') as f:
        data = pickle.load(f)

    input_image = face_recognition.load_image_file(input_image_path)
    input_locations = face_recognition.face_locations(input_image, number_of_times_to_upsample=2, model='hog')
    input_encodings = face_recognition.face_encodings(input_image, input_locations)

    if not input_encodings:
        print("[❌] No face found in input image.")
        return

    for face_encoding in input_encodings:
        matches = face_recognition.compare_faces(data['encodings'], face_encoding, tolerance=tolerance)
        face_distances = face_recognition.face_distance(data['encodings'], face_encoding)

        if any(matches):
            best_match_index = np.argmin(face_distances)
            name = data['names'][best_match_index]
            print(f"[✅] Match found: {name}")
        else:
            print("[❌] No match found.")

add_face_to_database('deb.jpeg', 'debnath')

recognize_face('deb1.jpeg')

recognize_face('1.jpg')

add_face_to_database('1.jpg', 'vivek')

recognize_face('2.jpg')
recognize_face('deb1.jpeg')