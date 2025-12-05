# University Admission Chatbot

This is a minimal Flask-based web chatbot that answers common university admission questions (deadlines, requirements, fees, scholarships, contact info).

Run locally on Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python app.py
```

If you encounter any issues installing dependencies, ensure your virtual environment is activated and run:

```powershell
pip install -r requirements.txt
```

Open your browser at `http://localhost:5000` after starting the app.

Notes:
- FAQs are now loaded from `faqs.csv` in the project root. Edit that file to add or update question keys and answers (CSV headers: `key,answer`).

