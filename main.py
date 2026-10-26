from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests, math, json

app = FastAPI(title="VoltRescue API", version="1.0.0")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

# Ollama config
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "gemma4"

def ollama_chat(messages: list[dict], stream: bool = False) -> str:
    payload = {"model": MODEL, "messages": messages, "stream": stream}
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

# Haversine
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))

# Host database - Pune residential charging hosts
HOSTS: list[dict] = [
    {"id": "H001", "name": "Arun Sharma",   "area": "Kothrud",         "lat": 18.5074, "lng": 73.8077, "port_types": ["Type 2", "15A Socket"], "speed_kw": 7.2, "rate_inr_per_kwh": 12, "active": True},
    {"id": "H002", "name": "Priya Desai",   "area": "Baner",           "lat": 18.5590, "lng": 73.7868, "port_types": ["CCS2", "Type 2"],        "speed_kw": 7.2, "rate_inr_per_kwh": 14, "active": True},
    {"id": "H003", "name": "Ravi Kulkarni", "area": "Wakad",           "lat": 18.5985, "lng": 73.7624, "port_types": ["Type 2"],                 "speed_kw": 3.3, "rate_inr_per_kwh": 10, "active": True},
    {"id": "H004", "name": "Meena Joshi",   "area": "Aundh",           "lat": 18.5579, "lng": 73.8080, "port_types": ["15A Socket"],             "speed_kw": 3.3, "rate_inr_per_kwh": 10, "active": True},
    {"id": "H005", "name": "Sanjay Patil",  "area": "Hinjewadi",       "lat": 18.5912, "lng": 73.7384, "port_types": ["CCS2"],                   "speed_kw": 7.2, "rate_inr_per_kwh": 13, "active": True},
    {"id": "H006", "name": "Anita More",    "area": "Pimpri",          "lat": 18.6279, "lng": 73.7998, "port_types": ["Type 2", "CCS2"],         "speed_kw": 7.2, "rate_inr_per_kwh": 12, "active": True},
    {"id": "H007", "name": "Deepak Nair",   "area": "Shivajinagar",    "lat": 18.5308, "lng": 73.8474, "port_types": ["15A Socket", "Type 2"],   "speed_kw": 3.3, "rate_inr_per_kwh": 11, "active": True},
    {"id": "H008", "name": "Kavita Rao",    "area": "Deccan Gymkhana", "lat": 18.5162, "lng": 73.8419, "port_types": ["Type 2"],                 "speed_kw": 7.2, "rate_inr_per_kwh": 13, "active": True},
    {"id": "H009", "name": "Nikhil Ghosh",  "area": "Viman Nagar",     "lat": 18.5679, "lng": 73.9143, "port_types": ["CCS2"],                   "speed_kw": 7.2, "rate_inr_per_kwh": 14, "active": False},
    {"id": "H010", "name": "Sunita Biswas", "area": "Hadapsar",        "lat": 18.5018, "lng": 73.9260, "port_types": ["Type 2", "15A Socket"],   "speed_kw": 3.3, "rate_inr_per_kwh": 10, "active": True},
    {"id": "H011", "name": "Rohit Sathe",   "area": "Magarpatta",      "lat": 18.5111, "lng": 73.9270, "port_types": ["CCS2", "Type 2"],         "speed_kw": 7.2, "rate_inr_per_kwh": 12, "active": True},
    {"id": "H012", "name": "Lalitha Menon", "area": "Kondhwa",         "lat": 18.4684, "lng": 73.8858, "port_types": ["15A Socket"],             "speed_kw": 3.3, "rate_inr_per_kwh": 10, "active": True},
    {"id": "H013", "name": "Vivek Tiwari",  "area": "Katraj",          "lat": 18.4527, "lng": 73.8625, "port_types": ["Type 2"],                 "speed_kw": 7.2, "rate_inr_per_kwh": 11, "active": True},
    {"id": "H014", "name": "Pooja Iyer",    "area": "Sinhagad Road",   "lat": 18.4810, "lng": 73.8240, "port_types": ["CCS2"],                   "speed_kw": 7.2, "rate_inr_per_kwh": 14, "active": True},
    {"id": "H015", "name": "Amit Wagh",     "area": "Warje",           "lat": 18.4895, "lng": 73.7960, "port_types": ["Type 2", "15A Socket"],   "speed_kw": 3.3, "rate_inr_per_kwh": 10, "active": True},
]

# Request models
class EmergencyRequest(BaseModel):
    user_id: str
    vehicle_model: str
    battery_percentage: float
    port_type: str
    lat: float
    lng: float

class ChatRequest(BaseModel):
    message: str

# POST /api/emergency-match
@app.post("/api/emergency-match")
def emergency_match(req: EmergencyRequest):
    nearby = []
    for h in HOSTS:
        if not h["active"]:
            continue
        if req.port_type not in h["port_types"]:
            continue
        dist = haversine(req.lat, req.lng, h["lat"], h["lng"])
        if dist <= 10.0:
            nearby.append({**h, "distance_km": round(dist, 2)})

    if not nearby:
        raise HTTPException(status_code=404, detail="No compatible charging hosts found within 10 km.")

    nearby.sort(key=lambda x: x["distance_km"])

    host_summary = "\n".join(
        f"- ID:{h['id']} | {h['name']} ({h['area']}) | {h['distance_km']} km | "
        f"{h['speed_kw']} kW | {h['port_types']} | Rs.{h['rate_inr_per_kwh']}/kWh"
        for h in nearby
    )

    system_prompt = (
        "You are VoltRescue AI, an emergency EV dispatch coordinator. "
        "Analyze stranded EV telemetry and available hosts, then respond ONLY with "
        "a single valid JSON object, no markdown, no explanation:\n"
        '{"selected_host_id": "", "priority_level": "LOW|MEDIUM|HIGH|CRITICAL", '
        '"estimated_charge_minutes": 0, "driver_message": "", "host_alert_message": ""}'
    )

    user_content = (
        f"STRANDED VEHICLE TELEMETRY:\n"
        f"  User: {req.user_id} | Vehicle: {req.vehicle_model}\n"
        f"  Battery: {req.battery_percentage}% | Port: {req.port_type}\n"
        f"  Location: ({req.lat}, {req.lng})\n\n"
        f"ELIGIBLE HOSTS (within 10 km, port-compatible):\n{host_summary}\n\n"
        f"Select the single best host. Estimate minutes to reach 30% battery from current "
        f"{req.battery_percentage}% assuming a 60 kWh usable battery pack. "
        f"Draft concise driver and host alert messages. Return ONLY the JSON."
    )

    try:
        raw = ollama_chat([
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ])
        clean = raw.strip().strip("```json").strip("```").strip()
        result = json.loads(clean)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")

    return {"ai_dispatch": result, "nearby_hosts": nearby}

# POST /api/chat
@app.post("/api/chat")
def ev_chat(req: ChatRequest):
    system_prompt = (
        "You are VoltRescue Copilot, a concise calm emergency assistant for stranded EV drivers in India. "
        "Provide short actionable advice on EV charging, range anxiety, finding help, and safety. "
        "Never suggest non-EV solutions. Keep replies under 120 words."
    )
    try:
        reply = ollama_chat([
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": req.message},
        ])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")

    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
