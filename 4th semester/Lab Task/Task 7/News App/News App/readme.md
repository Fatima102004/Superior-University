# News App (Flask backend)

This workspace contains a minimal Flask-based backend for a small news app.

Quick start

- Create a Python virtual environment and activate it (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirenments.txt
```

- Run the app:

```powershell
python app.py
```

This starts the server on `http://0.0.0.0:5000`.

Endpoints

- `GET /` — serves a minimal `index.html` template.
- `GET /api/news` — returns stored news items (local storage).
- `POST /api/news` — add a news item (JSON body: `title` required, `description`, `url`, `source`, `published_at` optional).
- `GET /api/news?source=newsapi` — fetches top headlines from NewsAPI.org if environment variable `NEWSAPI_KEY` is set.

Notes

- Local news are stored in `data/news.json`.
- To enable external fetches set `NEWSAPI_KEY` in your environment (obtain a free key at https://newsapi.org/) and then call `GET /api/news?source=newsapi`.
