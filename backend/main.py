from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import List
import json
from pydantic import BaseModel
from database import init_db, get_db, Incident
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
from ultralytics import YOLO
import asyncio
import os
import time
import random
import urllib.request
import json
import base64

# Load fine-tuned YOLO model if available, else fallback
model_path = os.path.join("..", "models", "best.pt")
model = YOLO(model_path) if os.path.exists(model_path) else YOLO('yolov8n.pt')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    await init_db()
    asyncio.create_task(voice_status_loop())
    yield

app = FastAPI(title="RAVEN Backend API", lifespan=lifespan)

# Allow dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

class StatusUpdate(BaseModel):
    message: str

class IncidentCreate(BaseModel):
    latitude: float
    longitude: float
    victim_count: int
    severity_score: float
    tier: str
    semantic_assessment: str | None = None

@app.post("/api/status_update")
async def broadcast_status(status: StatusUpdate):
    payload = {
        "id": "STATUS-UPDATE",
        "message": status.message
    }
    await manager.broadcast(json.dumps(payload))
    return {"status": "success"}

@app.post("/api/incident")
async def report_incident(incident: IncidentCreate, db: AsyncSession = Depends(get_db)):
    new_incident = Incident(
        latitude=incident.latitude,
        longitude=incident.longitude,
        victim_count=incident.victim_count,
        severity_score=incident.severity_score,
        tier=incident.tier,
        semantic_assessment=incident.semantic_assessment
    )
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    
    # Broadcast to all connected dashboard clients
    payload = {
        "id": new_incident.id,
        "latitude": new_incident.latitude,
        "longitude": new_incident.longitude,
        "victim_count": new_incident.victim_count,
        "severity_score": new_incident.severity_score,
        "tier": new_incident.tier,
        "semantic_assessment": new_incident.semantic_assessment,
        "timestamp": new_incident.timestamp.isoformat()
    }
    await manager.broadcast(json.dumps(payload))
    return {"status": "success", "incident_id": new_incident.id}

@app.get("/api/incidents")
async def get_incidents(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    result = await db.execute(select(Incident).order_by(Incident.timestamp.desc()).limit(50))
    incidents = result.scalars().all()
    return incidents

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

vlm_verified_time = 0
is_verifying = False

def check_vlm_sync(frame_bytes):
    global vlm_verified_time, is_verifying
    try:
        encoded_image = base64.b64encode(frame_bytes).decode('utf-8')
        payload = {
            "model": "moondream",
            "messages": [{
                "role": "user",
                "content": "Is there a VIOLENT CAR CRASH, COLLISION, or FLIPPED VEHICLE in this image? Answer strictly with YES or NO. If it is just normal cars driving, parked, or standing in traffic, you MUST answer NO.",
                "images": [encoded_image]
            }],
            "stream": False
        }
        req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text = res_data.get("message", {}).get("content", "").upper()
            if "YES" in text:
                vlm_verified_time = time.time()
    except Exception as e:
        print("VLM Error:", e)
    finally:
        is_verifying = False

current_status_tier = "Normal"

async def voice_status_loop():
    safe_phrases = [
        "Area secure. No anomalies detected.",
        "Patrol mode active. Traffic is normal.",
        "All clear. Monitoring sector.",
        "No accidents detected. Continuing patrol.",
        "System nominal. Safe conditions observed."
    ]
    while True:
        await asyncio.sleep(6) # Wait 6 seconds between announcements
        if current_status_tier == "Normal":
            msg = random.choice(safe_phrases)
        else:
            msg = f"Attention. {current_status_tier} incident detected. Monitoring situation."
            
        payload = {
            "id": "STATUS-UPDATE",
            "message": msg
        }
        await manager.broadcast(json.dumps(payload))

async def generate_frames(video_name: str):
    global is_verifying
    video_path = os.path.join("..", "dashboard", video_name)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return
    
    count = 0
    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            
        count += 1
        results = model(frame)
        
        # Determine accident state every frame to decide bounding box colors
        accident_detected = False
        temp_tier = "Normal"
        temp_severity = 0
        
        for box in results[0].boxes:
            conf = float(box.conf[0])
            if conf > 0.70:
                accident_detected = True
                cls = int(box.cls[0])
                name = model.names[cls] if cls in model.names else "unknown"
                if name == "severe":
                    temp_tier = "Critical"
                    temp_severity = max(temp_severity, 85)
                elif name == "moderate":
                    temp_tier = "Serious" if temp_tier != "Critical" else "Critical"
                    temp_severity = max(temp_severity, 60)
                else:
                    if cls in [0, 2, 3, 5, 7]:
                        temp_tier = "Serious"
                        temp_severity = max(temp_severity, 50)
        
        global current_status_tier
        is_verified = False
        if accident_detected:
            if time.time() - vlm_verified_time < 30:
                is_verified = True
            else:
                temp_tier = "Normal"
                temp_severity = 0
                if count % 15 == 0:
                    if not is_verifying:
                        is_verifying = True
                        ret, buffer = cv2.imencode('.jpg', frame)
                        asyncio.create_task(asyncio.to_thread(check_vlm_sync, buffer.tobytes()))
        
        # Draw custom bounding boxes directly on the frame
        annotated_frame = frame.copy()
        for box in results[0].boxes:
            conf = float(box.conf[0])
            if conf > 0.40:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                if conf > 0.70 and is_verified:
                    cls = int(box.cls[0])
                    name = model.names[cls] if cls in model.names else "unknown"
                    color = (0, 0, 255) # Red for confirmed accident
                    label = f"{name.upper()} ACCIDENT {conf:.2f}"
                else:
                    color = (0, 255, 0) # Green for normal vehicle
                    label = f"Normal {conf:.2f}"
                
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated_frame, label, (x1, max(y1 - 10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if count % 15 == 0:
            current_status_tier = temp_tier if is_verified else "Normal"
            
            assessment = "Normal traffic flow observed. No anomalies detected. Continuing routine patrol."
            if current_status_tier == "Critical":
                assessment = "Severe collision detected involving multiple vehicles. High probability of trapped occupants. Structural damage visible. Immediate medical intervention recommended."
            elif current_status_tier == "Serious":
                assessment = "Moderate collision detected. Vehicles obstructing traffic. Possible minor injuries. Deploying standard medical kit."
                
            payload = {
                "id": "LIVE-AI",
                "latitude": 12.9716,
                "longitude": 80.2437,
                "victim_count": 3 if current_status_tier == "Critical" else (1 if current_status_tier == "Serious" else 0),
                "severity_score": temp_severity if is_verified else 0,
                "tier": current_status_tier,
                "semantic_assessment": assessment,
                "timestamp": "LIVE STREAM"
            }
            await manager.broadcast(json.dumps(payload))

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        await asyncio.sleep(0.01)

@app.get("/api/video_feed")
async def video_feed(video: str = "drone_traffic.mp4"):
    return StreamingResponse(generate_frames(video), media_type="multipart/x-mixed-replace; boundary=frame")
