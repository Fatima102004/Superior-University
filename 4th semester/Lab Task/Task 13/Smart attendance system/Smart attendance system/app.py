from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
import os
from datetime import datetime
import pickle
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


known_faces = {}  
attendance_log = []
lock = threading.Lock()


face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
eyes_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'

face_cascade = cv2.CascadeClassifier(face_cascade_path)
eyes_cascade = cv2.CascadeClassifier(eyes_cascade_path)

if face_cascade.empty():
    print(f"Error: Could not load face cascade from {face_cascade_path}")
if eyes_cascade.empty():
    print(f"Error: Could not load eyes cascade from {eyes_cascade_path}")


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def extract_face_features(image):
    """
    Extracts face features with strict Boundary Checking to prevent crashes.
    This resolves the root cause of 'invalid vector subscript' errors.
    """
   
    img_h, img_w = image.shape[:2]
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    ay) better than 1.3
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) > 0:
       
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        (x, y, w, h) = faces[0]
        
       
        x = max(0, x)
        y = max(0, y)
        
       
        w = min(w, img_w - x)
        h = min(h, img_h - y)
        
       
        if w < 20 or h < 20:
            return None, None
            
        
        face_crop = image[y:y+h, x:x+w]
        
        try:
            
            hist = cv2.calcHist([face_crop], [0, 1, 2], None, [8, 8, 8], 
                               [0, 256, 0, 256, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            
            return hist, (x, y, x+w, y+h)
        except:
           
            return None, None
    
    return None, None

def load_known_faces():
    """Load known faces from pickle file"""
    global known_faces
    faces_file = 'known_faces.pkl'
    
    if os.path.exists(faces_file):
        try:
            with open(faces_file, 'rb') as f:
                known_faces = pickle.load(f)
        except EOFError:
            known_faces = {}

def save_known_faces():
    """Save known faces to pickle file"""
    with open('known_faces.pkl', 'wb') as f:
        pickle.dump(known_faces, f)

def match_face(face_features, threshold=3.0):
    """Match face features with known faces"""
    if not known_faces:
        return "Unknown", 1.0
    
    best_match = "Unknown"
    best_distance = float('inf')
    
    for name, known_features in known_faces.items():
        
        distance = cv2.norm(face_features, known_features, cv2.NORM_L2)
        if distance < best_distance:
            best_distance = distance
            best_match = name if distance < threshold else "Unknown"
    
    return best_match, best_distance

def mark_attendance(name):
    """Mark attendance for a person"""
    global attendance_log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    
    if attendance_log and attendance_log[-1]['name'] == name:
        try:
            last_time = datetime.strptime(attendance_log[-1]['time'], "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last_time).total_seconds() < 5:
                return False
        except ValueError:
            pass
    
    with lock:
        attendance_log.append({
            'name': name,
            'time': timestamp,
            'status': 'Present'
        })
    
    return True

def gen_frames():
    """Generate frames for video stream"""
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        print("Error: Could not open video source.")
        return

    process_this_frame = 0
    face_locations = []
    face_names = []
    face_distances = []
    
    while True:
        ret, frame = video_capture.read()
        
        if not ret:
            break
        
        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        
        if process_this_frame % 2 == 0:
            face_locations = []
            face_names = []
            face_distances = []
            
            try:
                face_features, bbox = extract_face_features(small_frame)
                
                if face_features is not None:
                    name, distance = match_face(face_features)
                    if name != "Unknown":
                        mark_attendance(name)
                    
                    face_locations.append(bbox)
                    face_names.append(name)
                    face_distances.append(distance)
            except Exception as e:
                print(f"Error in processing frame: {e}")
                pass
        
        process_this_frame += 1
        
        
        if face_locations:
            for (left, top, right, bottom), name, distance in zip(face_locations, face_names, face_distances):
                
                left *= 4
                top *= 4
                right *= 4
                bottom *= 4
                
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                label = f"{name} ({distance:.2f})" if name != "Unknown" else "Unknown"
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    with lock:
        return jsonify(attendance_log)

@app.route('/api/attendance/clear', methods=['POST'])
def clear_attendance():
    global attendance_log
    with lock:
        attendance_log = []
    return jsonify({'status': 'success', 'message': 'Attendance cleared'})

@app.route('/api/register-face', methods=['POST'])
def register_face():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'status': 'error', 'message': 'Missing file or name'}), 400
    
    file = request.files['file']
    name = request.form['name'].strip()
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    if not name:
        return jsonify({'status': 'error', 'message': 'Name cannot be empty'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    try:
        
        image = cv2.imread(filepath)
        if image is None:
            return jsonify({'status': 'error', 'message': 'Invalid image file'}), 400
        
        face_features, _ = extract_face_features(image)
        
        if face_features is None:
            return jsonify({'status': 'error', 'message': 'No face detected in image'}), 400
       
        with lock:
            known_faces[name] = face_features
            save_known_faces()
        
        return jsonify({'status': 'success', 'message': f'Face registered for {name}'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 400

@app.route('/api/registered-faces', methods=['GET'])
def get_registered_faces():
    return jsonify({
        'count': len(known_faces),
        'faces': list(known_faces.keys())
    })


@app.route('/api/delete-face', methods=['POST'])
def delete_face():
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({'message': 'Name is required'}), 400
            
        with lock:
            if name in known_faces:
                del known_faces[name]
                save_known_faces()
                return jsonify({'message': f'Successfully deleted {name}'})
            else:
                return jsonify({'message': 'User not found'}), 404
                
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    
    
if __name__ == '__main__':
    load_known_faces()
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)