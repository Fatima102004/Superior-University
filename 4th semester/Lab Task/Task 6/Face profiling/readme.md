# Face Profiling (Feature Measurements)

This small Flask app accepts an image, detects facial landmarks (via `dlib` or `face_recognition`), computes basic geometric measurements (eyes, nose, mouth, jawline), and maps them to a lightweight 16-type personality label.

Files updated/created:
- `app.py` — Flask backend with `/analyze` endpoint
- `requirenments.txt` — Python dependencies (note the file name is intentionally spelled as provided)
- `templates/index.html` — Front-end upload UI
- `static/script.js` and `static/style.css` — Front-end JS and styles

Requirements & setup
1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirenments.txt
```

3. Download the dlib 68-point shape predictor into the project root (optional but recommended for best accuracy):

 - http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

Download and extract `shape_predictor_68_face_landmarks.dat` into the same folder as `app.py`.

Running

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

Open `http://127.0.0.1:5000/` in your browser, upload an image, and click Analyze.

Notes
- dlib can be difficult to install on Windows; prebuilt wheels or conda are recommended if you encounter build issues.
- If `shape_predictor_68_face_landmarks.dat` is missing and `dlib` is present, the app will instruct you to download it. If `face_recognition` is installed it will try to use that as a fallback.
- The personality mapping is a simple deterministic mapping for demonstration and is not a psychological assessment.
