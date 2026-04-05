# 🇳🇬 Nigeria Location API — FastAPI

A FastAPI backend that serves all Nigerian States, LGAs, and Wards with cascading dropdown support and an embedded UI widget.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn main:app --reload

# 3. Open in browser
# Widget UI  → http://localhost:8000/
# API Docs   → http://localhost:8000/docs
# ReDoc      → http://localhost:8000/redoc
```

---

## 📁 Project Structure

```
nigeria_api/
├── main.py               # FastAPI app — all routes
├── requirements.txt
├── static/
│   └── index.html        # Embeddable dropdown widget UI
└── data/
    ├── states.json
    ├── lgas.json
    ├── wards.json
    ├── lgas-with-wards.json
    └── full.json
```

---

## 🔌 API Endpoints

### Dropdown (for `<select>` elements)

| Endpoint | Description |
|---|---|
| `GET /states/dropdown` | All 37 states as `[{value, label}]` |
| `GET /states/{state}/lgas/dropdown` | LGAs for a state |
| `GET /states/{state}/lgas/{lga}/wards/dropdown` | Wards for an LGA |

### Full metadata

| Endpoint | Description |
|---|---|
| `GET /states` | All states with capital, zone, coordinates |
| `GET /states/{state}` | Single state metadata |
| `GET /states/{state}/lgas` | All LGAs in a state with centroids |
| `GET /states/{state}/lgas/{lga}` | Single LGA metadata |
| `GET /states/{state}/lgas/{lga}/wards` | All wards with coordinates |

### Utility

| Endpoint | Description |
|---|---|
| `GET /search?q=Lagos` | Search across states, LGAs, wards |
| `GET /stats` | Dataset summary counts |
| `GET /` | Embedded dropdown widget (HTML) |

---

## 🖼️ Embed the Widget

Drop into any HTML page:

```html
<iframe
  src="http://yourserver.com/"
  width="100%"
  height="560"
  frameborder="0"
  style="border-radius:18px"
></iframe>
```

Or use the API directly in your JS:

```js
// Cascading dropdowns
const states = await fetch('/states/dropdown').then(r => r.json());
const lgas   = await fetch('/states/Lagos/lgas/dropdown').then(r => r.json());
const wards  = await fetch('/states/Lagos/lgas/Agege/wards/dropdown').then(r => r.json());
```

---

## 🛡️ Production Tips

- Set `allow_origins` in CORSMiddleware to your actual domain
- Serve behind **nginx** or **Caddy** as a reverse proxy
- The data is loaded once at startup and cached in memory — no DB needed
- Deploy on **Railway**, **Render**, **Fly.io**, or any VPS

---

## 📊 Dataset

- **37** States (including FCT)
- **780** Local Government Areas
- **8,905** Wards with lat/long coordinates

---

## UI URL

You can click on this link to open the UI
***https://nigeria-api.onrender.com/***
