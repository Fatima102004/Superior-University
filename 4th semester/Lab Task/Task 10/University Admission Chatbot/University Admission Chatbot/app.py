from flask import Flask, render_template, request, jsonify
import csv
import os
import re

app = Flask(__name__)

def load_faqs_from_csv():
    faqs = {}
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faqs.csv")
    print(f"DEBUG: Looking for CSV at: {csv_path}")
    
    try:
        with open(csv_path, newline='', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                key = (row.get('key') or row.get('Key') or '').strip().lower()
                answer = (row.get('answer') or row.get('Answer') or '').strip()
                if key and answer:
                    faqs[key] = answer
        print(f"DEBUG: Successfully loaded {len(faqs)} FAQs.")
    except Exception as exc:
        print(f"DEBUG: Error loading CSV: {exc}")
        
    return faqs

FAQS = load_faqs_from_csv()
FAQ_KEYS = sorted(FAQS.keys(), key=len, reverse=True)

def get_reply(message: str) -> str:
    text = message.lower()

    if any(g in text for g in ("hi", "hello", "hey", "greetings")):
        return "Hello! I'm the University Admission Chatbot. How can I help you today?"

    if re.search(r'\b(thank|thanks)\b', text):
        return "You're welcome! If you have more questions, just ask."

    for key in FAQ_KEYS:
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, text):
            return FAQS[key]

    if "when" in text and "apply" in text:
        return FAQS.get("deadline", "Please check our website for specific dates.")
    
    if "how" in text and "much" in text:
        return FAQS.get("tuition", "Tuition details are available on the finance page.")

    return (
        "I'm not sure about that specific detail. "
        "Try asking about deadlines, tuition, housing, programs, scholarships, or international admissions."
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    
    if not message or not message.strip():
        return jsonify({"reply": "Please type a question or message."})

    reply = get_reply(message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)