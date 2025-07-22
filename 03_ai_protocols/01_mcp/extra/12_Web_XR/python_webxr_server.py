import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebXR_SUPPORT_SERVER - %(levelname)s - %(message)s')

app = FastAPI(
    title="WebXR Support Server",
    description="A conceptual Python FastAPI server to support a WebXR client application.",
    version="0.1.0"
)

# --- Static files (for serving WebXR HTML, JS, assets) ---
# Create a dummy static directory and a basic HTML file if they don't exist
STATIC_DIR = "static_webxr"
INDEX_HTML = os.path.join(STATIC_DIR, "index_webxr.html")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    logging.info(f"Created static directory: {STATIC_DIR}")

if not os.path.exists(INDEX_HTML):
    with open(INDEX_HTML, "w") as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Basic WebXR Page</title>
    <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f0f0; font-family: sans-serif; }
        #info { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; }
        button { padding: 15px 25px; font-size: 1.2em; cursor: pointer; }
    </style>
</head>
<body>
    <div id="info">WebXR Support Server is running. This is a placeholder page.</div>
    <button id="xr-button">Enter XR (Not Implemented)</button>
    <canvas id="xr-canvas" style="display: none;"></canvas> 

    <script>
        // Basic WebXR setup would go here (e.g., using Three.js or Babylon.js)
        // This is a very simplified placeholder.
        const xrButton = document.getElementById('xr-button');
        const infoDiv = document.getElementById('info');

        if (navigator.xr) {
            infoDiv.textContent = "WebXR API is available.";
            xrButton.addEventListener('click', () => {
                infoDiv.textContent = "XR button clicked. Implement session request here.";
                // Example: navigator.xr.requestSession('immersive-vr').then(...);
            });
        } else {
            infoDiv.textContent = "WebXR API not available in this browser.";
            xrButton.disabled = true;
        }
    </script>
</body>
</html>
""")
        logging.info(f"Created basic WebXR HTML file: {INDEX_HTML}")

app.mount(f"/{STATIC_DIR}", StaticFiles(directory=STATIC_DIR), name="static_webxr_files")

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse, summary="Serve the main WebXR client page")
async def get_main_webxr_page():
    """
    Serves the `index_webxr.html` file which would contain the WebXR client-side logic.
    """
    logging.info(f"Serving WebXR client page: {INDEX_HTML}")
    if os.path.exists(INDEX_HTML):
        with open(INDEX_HTML, "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        logging.error(f"{INDEX_HTML} not found!")
        raise HTTPException(status_code=404, detail="WebXR client page (index_webxr.html) not found.")

@app.get("/api/xr-config", summary="Get configuration for the WebXR scene")
async def get_xr_config():
    """
    A conceptual endpoint to provide initial configuration or scene data 
    to the WebXR client.
    """
    logging.info("Client requested XR configuration.")
    return {
        "sceneName": "DACA_Agent_Interaction_Space_v1",
        "environment": "default_grid",
        "lighting": {"type": "ambient", "intensity": 0.8},
        "startPosition": {"x": 0, "y": 1.6, "z": 2},
        "agentModels": [
            {"id": "agent_alpha", "modelUrl": f"/{STATIC_DIR}/assets/agent_alpha.glb", "voice": "neutral"},
            {"id": "agent_beta", "modelUrl": f"/{STATIC_DIR}/assets/agent_beta.glb", "voice": "friendly"}
        ],
        "instructions": "Interact with the agents using voice or controllers."
    }

@app.post("/api/xr-event", summary="Receive an event from the WebXR client")
async def post_xr_event(event_data: dict):
    """
    A conceptual endpoint for the WebXR client to send interaction data or events
    to the server (e.g., user selected an object, voice command recognized by client).
    The server (DACA agent) could then process this and update state or trigger actions.
    """
    logging.info(f"Received XR event from client: {event_data}")
    # Example: Process event, update Dapr state, publish to Dapr pub/sub, etc.
    # For now, just echo it back with a server timestamp.
    return {
        "status": "event_received",
        "original_event": event_data,
        "server_timestamp": asyncio.get_event_loop().time()
    }

# --- Main execution ---
if __name__ == "__main__":
    logging.info("Starting WebXR Support Server using Uvicorn...")
    # Create dummy asset directory for the example config
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        logging.info(f"Created dummy assets directory: {assets_dir}")
        # Create dummy GLB files mentioned in config to avoid 404s if client tries to fetch
        with open(os.path.join(assets_dir, "agent_alpha.glb"), "w") as f: f.write("dummy_glb_content_alpha")
        with open(os.path.join(assets_dir, "agent_beta.glb"), "w") as f: f.write("dummy_glb_content_beta")

    uvicorn.run(app, host="0.0.0.0", port=8008, log_level="info")

    # To run:
    # 1. pip install uvicorn fastapi
    #    (or `uv pip install uvicorn fastapi`)
    # 2. python python_webxr_server.py
    # 3. Open your browser to http://localhost:8008/
    # The server will create a `static_webxr` directory with `index_webxr.html` and `assets`. 