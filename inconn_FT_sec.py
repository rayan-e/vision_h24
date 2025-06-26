import cv2
import base64
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

# Initialisation de la webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Impossible d'ouvrir la caméra")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue

            # Encodage en JPEG et conversion en base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_str = base64.b64encode(buffer).decode('utf-8')

            # Envoi au client via WebSocket
            await websocket.send_text(img_str)
            await asyncio.sleep(0.1)  # Limite à 10 FPS
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/", response_class=HTMLResponse)
async def home():
    html_path = os.path.join("templates", "FT_sec.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h1>Fichier HTML non trouvé</h1>", status_code=404)
    with open(html_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Libérer la caméra à l'arrêt de l'application
@app.on_event("shutdown")
def shutdown_event():
    cap.release()
