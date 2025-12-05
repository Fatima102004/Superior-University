import io
import os
import math
import sys
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import cv2

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Load OpenCV cascade classifiers for face and feature detection
cascade_path = cv2.data.haarcascades
face_cascade = cv2.CascadeClassifier(cascade_path + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cascade_path + 'haarcascade_eye.xml')

print(f"Face cascade loaded: {not face_cascade.empty()}", file=sys.stderr)
print(f"Eye cascade loaded: {not eye_cascade.empty()}", file=sys.stderr)


def read_image_from_file(file_storage):
	try:
		data = file_storage.read()
		print(f"Read {len(data)} bytes from file", file=sys.stderr)
		arr = np.frombuffer(data, np.uint8)
		img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
		print(f"Image shape: {img.shape if img is not None else 'None'}", file=sys.stderr)
		return img
	except Exception as e:
		print(f"Error in read_image_from_file: {e}", file=sys.stderr)
		import traceback
		traceback.print_exc(file=sys.stderr)
		return None


def detect_landmarks_opencv(img):
	"""Detect face and basic features using OpenCV Haar cascades."""
	if img is None:
		print("Error: img is None", file=sys.stderr)
		return None
	
	try:
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)
		print(f"Detected {len(faces)} face(s)", file=sys.stderr)

		if len(faces) == 0:
			return None

		# cast to plain Python ints to avoid numpy types in JSON
		x, y, w, h = map(int, faces[0])
		roi_gray = gray[y:y + h, x:x + w]
		roi_color = img[y:y + h, x:x + w]

		# Detect eyes within face region
		eyes = eye_cascade.detectMultiScale(roi_gray)
		print(f"Detected {len(eyes)} eye(s)", file=sys.stderr)

		# Create synthetic landmarks from detected features
		points = []
		# Add face box corners and midpoints as landmarks (use int())
		points.append([int(x), int(y)])  # top-left
		points.append([int(x + w), int(y)])  # top-right
		points.append([int(x + w), int(y + h)])  # bottom-right
		points.append([int(x), int(y + h)])  # bottom-left
		points.append([int(x + w // 2), int(y)])  # top-center
		points.append([int(x + w // 2), int(y + h)])  # bottom-center
		points.append([int(x), int(y + h // 2)])  # left-center
		points.append([int(x + w), int(y + h // 2)])  # right-center
		points.append([int(x + w // 2), int(y + h // 2)])  # center

		# Add eye centers if detected (cast elements to int)
		for (ex, ey, ew, eh) in eyes[:2]:
			ex, ey, ew, eh = map(int, (ex, ey, ew, eh))
			points.append([int(x + ex + ew // 2), int(y + ey + eh // 2)])

		print(f"Created {len(points)} landmarks", file=sys.stderr)
		return points if len(points) > 0 else None
	except Exception as e:
		print(f"Error in detect_landmarks_opencv: {e}", file=sys.stderr)
		import traceback
		traceback.print_exc(file=sys.stderr)
		return None


def dist(a, b):
	try:
		return float(math.hypot(float(a[0])-float(b[0]), float(a[1])-float(b[1])))
	except (TypeError, IndexError, ValueError):
		return 0.0


def compute_measurements(points):
	"""Compute geometric measurements from detected landmarks."""
	measurements = {}
	n = len(points)
	measurements['landmark_count'] = n
	
	if n >= 9:
		# Use detected face box and feature points
		# points[0-3] are face corners, points[4-8] are midpoints, points[9+] are eyes
		face_width = dist(points[1], points[0])  # top-right to top-left
		face_height = dist(points[0], points[3])  # top-left to bottom-left
		jaw_width = face_width
		
		measurements.update({
			'face_width': face_width,
			'face_height': face_height,
			'jaw_width': jaw_width,
			'aspect_ratio': face_width / face_height if face_height > 0 else 0
		})
		
		# If eyes were detected, add interpupillary distance
		if n >= 11:
			interpupillary = dist(points[9], points[10])
			measurements['interpupillary'] = interpupillary
	
	return measurements


PERSONALITY_TYPES = [
	'INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP',
	'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP'
]


def map_profile(measurements):
	# Create a deterministic mapping from measurements -> one of 16 types.
	keys = ['interpupillary', 'nose_width', 'mouth_width', 'jaw_width', 'face_height']
	vals = []
	for k in keys:
		v = measurements.get(k, 0.0)
		vals.append(v)
	s = int(sum([int(x*100) for x in vals if x is not None]))
	idx = s % 16
	return {
		'type': PERSONALITY_TYPES[idx],
		'description': f'Profile based on geometric features (index {idx}). This is a light, non-clinical mapping to the 16-type labels.'
	}


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
	if 'image' not in request.files:
		return jsonify({'error': 'no image file uploaded'}), 400
	file = request.files['image']
	if file.filename == '':
		return jsonify({'error': 'empty filename'}), 400
	try:
		img = read_image_from_file(file)
		if img is None or img.size == 0:
			return jsonify({'error': 'invalid image data'}), 400
		
		points = detect_landmarks_opencv(img)

		if points is None:
			return jsonify({'error': 'no face detected'}), 400

		measurements = compute_measurements(points)
		profile = map_profile(measurements)

		return jsonify({'measurements': measurements, 'profile': profile, 'landmarks': points, 'detector': 'opencv'})
	except Exception as e:
		import traceback
		traceback.print_exc()
		return jsonify({'error': 'internal error', 'message': str(e)}), 500


if __name__ == '__main__':
	app.run(debug=False, use_reloader=False)
