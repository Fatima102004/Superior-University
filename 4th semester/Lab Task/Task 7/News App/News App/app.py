from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import json
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'news.json')

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

def ensure_data_dir():
    data_dir = os.path.dirname(DATA_PATH)
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    if not os.path.isfile(DATA_PATH):
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_news():
    ensure_data_dir()
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_news(news_list):
    ensure_data_dir()
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/news', methods=['GET'])
def get_news():
    """Return stored news; optionally fetch from NewsAPI."""
    source = request.args.get('source', '').lower()
    
    # Optional: Fetch from External API if key is present
    if source == 'newsapi':
        key = os.environ.get('NEWSAPI_KEY')
        if not key:
            return jsonify({'error': 'NEWSAPI_KEY not set'}), 400
        params = {'apiKey': key, 'language': 'en', 'pageSize': 10}
        try:
            resp = requests.get('https://newsapi.org/v2/top-headlines', params=params, timeout=10)
            if resp.status_code != 200:
                return jsonify({'error': 'external fetch failed', 'details': resp.text}), 502
            data = resp.json()
            articles = data.get('articles', [])
            normalized = []
            for a in articles:
                normalized.append({
                    'id': None,
                    'title': a.get('title'),
                    'description': a.get('description'),
                    'url': a.get('url'),
                    'source': (a.get('source') or {}).get('name'),
                    'published_at': a.get('publishedAt')
                })
            return jsonify({'source': 'newsapi', 'articles': normalized})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Default: Return Local News
    stored = load_news()
    return jsonify({'source': 'local', 'articles': stored})

@app.route('/api/news', methods=['POST'])
def add_news():
    """Add a news item to local storage."""
    if not request.is_json:
        return jsonify({'error': 'expected application/json'}), 415
    payload = request.get_json()
    title = payload.get('title')
    
    if not title:
        return jsonify({'error': 'title is required'}), 400
    
    description = payload.get('description')
    url = payload.get('url')
    source = payload.get('source', 'User Submitted')
    published_at = payload.get('published_at') or datetime.utcnow().isoformat() + 'Z'

    news_list = load_news()
    # Assign ID
    next_id = (max([n.get('id') or 0 for n in news_list]) + 1) if news_list else 1
    item = {
        'id': next_id,
        'title': title,
        'description': description,
        'url': url,
        'source': source,
        'published_at': published_at
    }
    news_list.insert(0, item)
    save_news(news_list)
    return jsonify({'ok': True, 'item': item}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)