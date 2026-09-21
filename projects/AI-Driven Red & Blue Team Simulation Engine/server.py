from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json
import random
import numpy as np
from sklearn.ensemble import IsolationForest
import sqlite3
import io
import csv

app = FastAPI()

# ==========================================
# 1. DATABASE INITIALIZATION
# ==========================================
def init_db():
    print("Initializing SQLite Database...")
    conn = sqlite3.connect("soc_logs.db")
    cursor = conn.cursor()
    # Create a table to store our cyber attacks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attacks (
            id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip TEXT,
            origin TEXT,
            threat_name TEXT,
            mitre TEXT,
            ai_score REAL,
            is_manual BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()
    print("Database Ready.")

def log_attack_to_db(attack):
    # This function saves a single attack to the database
    conn = sqlite3.connect("soc_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attacks (id, ip, origin, threat_name, mitre, ai_score, is_manual)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (attack['id'], attack['ip'], attack['originCountry'], 
          attack['threatName'], attack['threatMitre'], 
          attack['aiScore'], attack['isManual']))
    conn.commit()
    conn.close()

init_db() # Run this when the server starts!

# ==========================================
# 2. MACHINE LEARNING INITIALIZATION
# ==========================================
print("Initializing Machine Learning Model (Isolation Forest)...")
normal_traffic = np.array([
    [443, 12.5, 5], [80, 8.2, 2], [443, 15.1, 8], [443, 11.0, 4],
    [80, 5.5, 1], [443, 18.2, 10], [80, 9.1, 3], [443, 14.4, 6]
])

ai_model = IsolationForest(contamination=0.2, random_state=42)
ai_model.fit(normal_traffic)
print("AI Model Trained and Ready for Inference.")

# ==========================================
# 3. THREAT DATA
# ==========================================
THREATS = [
    {"name": "SSH Brute-Force", "mitre": "T1110", "color": "#ff3366"},
    {"name": "Port Sweep", "mitre": "T1046", "color": "#00ccff"},
    {"name": "DDoS SYN Flood", "mitre": "T1498", "color": "#ff9900"},
    {"name": "SQL Injection", "mitre": "T1190", "color": "#cc33ff"},
    {"name": "Log4Shell Exploit", "mitre": "T1190.005", "color": "#ff0033"},
    {"name": "Zero-Day Payload", "mitre": "T1106", "color": "#00ff80"}
]
ORIGINS = [
    {"country": "Russia", "lat": 61.52, "lng": 105.31},
    {"country": "China", "lat": 35.86, "lng": 104.19},
    {"country": "North Korea", "lat": 40.33, "lng": 127.51},
    {"country": "Iran", "lat": 32.42, "lng": 53.68}
]
TARGETS = [
    {"name": "AWS us-east-1", "lat": 38.89, "lng": -77.03},
    {"name": "Azure West Europe", "lat": 52.37, "lng": 4.89}
]

# ==========================================
# 4. API ENDPOINTS
# ==========================================
@app.get("/")
async def get():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: index.html not found!</h1>")

# NEW ENDPOINT: Download the database as a CSV file
@app.get("/export")
async def export_logs():
    conn = sqlite3.connect("soc_logs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp (UTC)", "IP Address", "Origin", "Threat Name", "MITRE", "AI Score", "Is Manual"])
    writer.writerows(rows)
    output.seek(0)
    
    return StreamingResponse(
        output, 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=soc_database_export.csv"}
    )

# ==========================================
# 5. WEBSOCKET PIPELINE
# ==========================================
@app.websocket("/ws/threats")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Dashboard connected via WebSocket!")
    
    async def generate_background_traffic():
        try:
            while True:
                await asyncio.sleep(random.uniform(0.5, 1.5)) 
                origin = random.choice(ORIGINS)
                target = random.choice(TARGETS)
                threat = random.choice(THREATS)
                
                packet_features = np.array([[443, random.uniform(5.0, 15.0), random.uniform(1.0, 5.0)]])
                raw_score = ai_model.decision_function(packet_features)[0]
                ai_score = round(max(10.0, min(49.9, 50 - (float(raw_score) * 100))), 1)
                
                attack_data = {
                    "id": str(random.randint(10000, 99999)),
                    "ip": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    "originCountry": origin["country"],
                    "threatName": threat["name"],
                    "threatMitre": threat["mitre"],
                    "color": threat["color"],
                    "aiScore": ai_score,
                    "isAnomaly": False,
                    "isManual": False,
                    "startLat": origin["lat"] + random.uniform(-2, 2),
                    "startLng": origin["lng"] + random.uniform(-2, 2),
                    "endLat": target["lat"],
                    "endLng": target["lng"]
                }
                
                log_attack_to_db(attack_data) # Save to Database!
                await websocket.send_text(json.dumps(attack_data))
        except asyncio.CancelledError:
            pass

    bg_task = asyncio.create_task(generate_background_traffic())

    try:
        while True:
            incoming_data = await websocket.receive_text()
            request = json.loads(incoming_data)
            chosen_threat_name = request.get("threatName", "SQL Injection")
            
            origin = random.choice(ORIGINS)
            target = random.choice(TARGETS)
            threat = next((t for t in THREATS if t["name"] == chosen_threat_name), THREATS[0])
            
            if threat["name"] == "Port Sweep":
                packet_features = np.array([[random.randint(1000, 9000), 1.2, 50]]) 
            elif threat["name"] == "DDoS SYN Flood":
                packet_features = np.array([[80, 0.5, 5000]]) 
            elif threat["name"] == "SSH Brute-Force":
                packet_features = np.array([[22, 5.0, 20]]) 
            else:
                packet_features = np.array([[443, random.uniform(50, 200), random.uniform(20, 50)]]) 
                
            raw_score = ai_model.decision_function(packet_features)[0]
            ai_score = round(max(85.0, min(99.9, 50 + (abs(float(raw_score)) * 100))), 1)
            
            attack_data = {
                "id": str(random.randint(10000, 99999)),
                "ip": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "originCountry": origin["country"],
                "threatName": threat["name"],
                "threatMitre": threat["mitre"],
                "color": "#b700ff", 
                "aiScore": ai_score,
                "isAnomaly": True,  
                "isManual": True,
                "startLat": origin["lat"] + random.uniform(-2, 2),
                "startLng": origin["lng"] + random.uniform(-2, 2),
                "endLat": target["lat"],
                "endLng": target["lng"]
            }
            
            log_attack_to_db(attack_data) # Save to Database!
            await websocket.send_text(json.dumps(attack_data))
            
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        bg_task.cancel()
