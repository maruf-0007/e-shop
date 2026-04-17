# e-shop POS — Deployment Guide

## Project Structure
```
PRODB/
├── backend/          ← FastAPI backend
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── requirements.txt
├── frontend/
│   └── index.html    ← Single-page frontend
├── Procfile          ← For Railway/Render
└── DEPLOY.md
```

## Option 1: Railway (Easiest — Free tier available)

1. Go to https://railway.app and sign up (free)
2. Click "New Project" → "Deploy from GitHub repo"
3. Push your project to GitHub first:
   ```bash
   git init
   git add .
   git commit -m "e-shop POS initial commit"
   git remote add origin https://github.com/YOUR_USER/eshop-pos.git
   git push -u origin main
   ```
4. In Railway, select your repo
5. Railway auto-detects the `Procfile` and deploys
6. Go to Settings → Variables → add `DATABASE_URL` (or leave blank for SQLite)
7. Your app gets a public URL like `https://eshop-pos-production.up.railway.app`
8. **Update `const API` in `frontend/index.html`** to your Railway URL

---

## Option 2: Render (Free tier available)

1. Go to https://render.com and sign up
2. New → "Web Service" → connect GitHub repo
3. Build Command: `pip install -r backend/requirements.txt`
4. Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Set env var `DATABASE_URL` if using MySQL/Postgres, otherwise SQLite is used automatically
6. Deploy — you get a URL like `https://eshop-pos.onrender.com`
7. **Update `const API` in `frontend/index.html`** to your Render URL

---

## Option 3: Run Locally

```bash
cd PRODB
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```
Backend runs at http://127.0.0.1:8000
Open `frontend/index.html` in your browser.

---

## Frontend Hosting (for the HTML file)

The frontend is a single `index.html` file. Host it for free on:
- **Netlify**: Drag & drop the `frontend/` folder at https://netlify.com
- **GitHub Pages**: Push to GitHub, enable Pages on the repo
- **Vercel**: Same as Netlify

**Important**: After deploying the backend, edit `frontend/index.html` line ~830:
```js
const API = 'https://YOUR-BACKEND-URL.railway.app';  // ← change this
```

---

## Database Notes
- **SQLite** (default): Works out of the box, data stored in `eshop.db` file. Good for small deployments.
- **MySQL/PostgreSQL**: Set `DATABASE_URL` environment variable on your host.
