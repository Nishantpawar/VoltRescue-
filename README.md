# VoltRescue - Emergency P2P EV Charging Network

> **Stranded with a dying battery? VoltRescue connects you to the nearest residential charger in seconds, powered entirely by local AI.**

---

## Concept

VoltRescue is a peer-to-peer emergency EV charging dispatch platform built for Indian EV drivers. When a vehicle runs critically low on battery, the driver broadcasts an SOS with their telemetry. A local Gemma 4 AI model (running on-device via Ollama) matches them to the closest compatible residential charger, estimates time to reach 30% charge, and auto-drafts alerts for both driver and host - all with zero cloud dependency.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI + Uvicorn (Python) |
| **AI Engine** | Ollama (local) - Model: `gemma4` |
| **Distance** | Pure Python Haversine formula |
| **Frontend** | Vanilla HTML/CSS/JS - No framework |
| **Styling** | Tailwind CSS (CDN) + FontAwesome 6 |
| **Animation** | Procedural BeamsBackground canvas (`requestAnimationFrame`) |
| **Data** | 15 Pune residential charging hosts (in-memory) |

---

## Prerequisites

1. **Python 3.11+** installed
2. **Ollama** installed and running locally
3. **Gemma 4** model pulled:

```bash
ollama pull gemma4
ollama serve   # keep running in a separate terminal
```

---

## Setup & Launch

### 1. Enter the project directory

```bash
cd VoltRescue
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the server

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Open the app

```
http://127.0.0.1:8000
```

---

## Project Structure

```
VoltRescue/
├── main.py              # FastAPI app - endpoints + Ollama integration
├── static/
│   └── index.html       # Full UI: beams canvas, SOS dispatch, copilot chat
├── requirements.txt     # Pinned Python dependencies
├── .gitignore
└── README.md
```

---

## API Endpoints

### `POST /api/emergency-match`

Accepts EV telemetry, runs Haversine proximity filter (10 km radius), then calls Gemma 4 to select the optimal host.

**Request:**
```json
{
  "user_id": "driver_001",
  "vehicle_model": "Tata Nexon EV Max",
  "battery_percentage": 8,
  "port_type": "Type 2",
  "lat": 18.5204,
  "lng": 73.8567
}
```

**Response:**
```json
{
  "ai_dispatch": {
    "selected_host_id": "H007",
    "priority_level": "CRITICAL",
    "estimated_charge_minutes": 92,
    "driver_message": "Head to Deepak Nair in Shivajinagar. 2.1 km away.",
    "host_alert_message": "Emergency EV arriving in ~8 min. Battery at 8%."
  },
  "nearby_hosts": ["..."]
}
```

### `POST /api/chat`

EV emergency copilot. Ask anything about your situation.

**Request:** `{ "message": "Can I charge on a 15A socket safely?" }`

**Response:** `{ "reply": "Yes, a 15A socket provides ~3.3 kW..." }`

---

## UI Features

- **Animated Beams Canvas** - 30 procedural light beams at -35 degrees with pulsing opacity and cyan/teal gradients, `blur(30px)` filter
- **Live Battery Meter** - tri-color (green to amber to red at 15% or below)
- **Glassmorphic Cards** - frosted-glass panels with depth shadows
- **Gemma 4 Copilot** - full chat with quick chips, typing indicator, auto-scroll
- **Priority Dispatch Badge** - CRITICAL / HIGH / MEDIUM / LOW color-coded from AI output

---

## Privacy

All AI inference runs **100% locally** via Ollama. No data leaves your machine. No API keys. No cloud calls.

---

*Built for the Indian EV community.*
