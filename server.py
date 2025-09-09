from fastapi import FastAPI, Body, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Artwork Sequencer Server")

# Allow browser access from anywhere (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)
HTML_PATH = TEMPLATES_DIR / "web_sequencer.html"
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data")).resolve()
DATA_DIR.mkdir(exist_ok=True)

# In-memory storage for viewer metadata
viewers: Dict[str, Dict[str, Any]] = {}
results: Dict[str, Dict[str, Any]] = {}

# Cleanup configuration
CLEANUP_INTERVAL_HOURS = 24  # Run cleanup every 24 hours
DATA_RETENTION_DAYS = 30  # Keep data for 30 days
MAX_STORAGE_ITEMS = 10000  # Maximum items to store (prevent memory issues)

@app.get("/")
def root():
    landing_html_path = TEMPLATES_DIR / "landing.html"
    if landing_html_path.exists():
        with open(landing_html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    else:
        # Fallback if template not found
        return JSONResponse({"error": "Landing page template not found"}, status_code=404)

@app.get("/app")
def app_page():
    if not HTML_PATH.exists():
        return JSONResponse({"error": "web_sequencer.html not found"}, status_code=404)
    return FileResponse(str(HTML_PATH))

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "viewers": len(viewers), 
        "results": len(results),
        "retention_days": DATA_RETENTION_DAYS,
        "max_items": MAX_STORAGE_ITEMS
    }

# API Endpoints for frontend-backend separation
@app.post("/api/create-viewer")
async def create_viewer(data: dict = Body(...)):
    """Create a shareable viewer link with untraceable ID"""
    viewer_id = str(uuid.uuid4())
    
    # Generate viewer HTML
    viewer_html = generate_viewer_html_with_data(data)
    
    # Save HTML to file
    viewer_file_path = DATA_DIR / f"viewer_{viewer_id}.html"
    with open(viewer_file_path, "w", encoding="utf-8") as f:
        f.write(viewer_html)
    
    # Store metadata
    viewers[viewer_id] = {
        "created_at": datetime.now().isoformat(),
        "file_path": str(viewer_file_path)
    }
    
    return {
        "viewer_id": viewer_id, 
        "url": f"/viewer/{viewer_id}",
        "full_url": f"{data.get('base_url', '')}/viewer/{viewer_id}"
    }

@app.get("/viewer/{viewer_id}")
async def get_viewer(viewer_id: str):
    """Serve the viewer page"""
    if viewer_id not in viewers:
        return JSONResponse({"error": "Viewer not found"}, status_code=404)
    
    viewer_metadata = viewers[viewer_id]
    viewer_file_path = Path(viewer_metadata["file_path"])
    
    if viewer_file_path.exists():
        return FileResponse(str(viewer_file_path))
    else:
        return JSONResponse({"error": "Viewer file not found"}, status_code=404)


@app.post("/api/save-result")
async def save_result(data: dict = Body(...)):
    """Save result data and return ID for retrieval"""
    result_id = str(uuid.uuid4())
    results[result_id] = {
        "data": data,
        "created_at": datetime.now().isoformat(),
    }
    return {"result_id": result_id}

@app.get("/api/result/{result_id}")
async def get_result(result_id: str):
    """Get saved result data"""
    if result_id not in results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return results[result_id]["data"]

@app.post("/api/generate-image")
async def generate_image(data: dict = Body(...)):
    """Generate final image from placements data"""
    # This would handle image generation server-side if needed
    # For now, return the data as the frontend handles it
    return {"status": "success", "message": "Image generation handled client-side"}

@app.post("/api/generate-report")
async def generate_report(data: dict = Body(...)):
    """Generate report from placements data"""
    mode = data.get("mode", "single")
    use_pics = data.get("use_pics", False)
    num_arts = data.get("num_arts", 8)
    placements = data.get("placements", [])
    
    lines = []
    lines.append("Artwork SEQUENCING REPORT")
    lines.append("=" * 50)
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Road Type: {'Two Way' if mode == 'two' else 'Single Way'}")
    lines.append(f"Use Pictures: {'Yes' if use_pics else 'No'}")
    lines.append(f"Unique Artworks: {num_arts}")
    lines.append("")
    
    counts1, counts2 = {}, {}
    for p in placements:
        a1 = p.get("s1_icon") or p.get("s1_num")
        if a1:
            counts1[str(a1)] = counts1.get(str(a1), 0) + 1
        
        a2 = p.get("s2_icon") or p.get("s2_num")
        if a2:
            counts2[str(a2)] = counts2.get(str(a2), 0) + 1
    
    lines.append("Artwork Requirements:")
    lines.append("-" * 50)
    for i in range(1, num_arts + 1):
        i_str = str(i)
        total = counts1.get(i_str, 0) + counts2.get(i_str, 0)
        if mode == "two":
            lines.append(f"Artwork #{i}: {total} copies (Side 1: {counts1.get(i_str, 0)}, Side 2: {counts2.get(i_str, 0)})")
        else:
            lines.append(f"Artwork #{i}: {counts1.get(i_str, 0)} copies")
    
    return {"report": "\n".join(lines)}

@app.get("/api/download/{result_id}/{file_type}")
async def download_file(result_id: str, file_type: str):
    """Download generated files"""
    if result_id not in results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    data = results[result_id]["data"]
    
    if file_type == "report":
        report = data.get("report", "")
        return Response(
            content=report,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=report.txt"}
        )
    elif file_type == "image":
        # Handle image download if stored server-side
        image_data = data.get("image_data", "")
        if image_data.startswith("data:image/png;base64,"):
            image_data = image_data.replace("data:image/png;base64,", "")
        
        try:
            image_bytes = base64.b64decode(image_data)
            return Response(
                content=image_bytes,
                media_type="image/png",
                headers={"Content-Disposition": "attachment; filename=final.png"}
            )
        except:
            raise HTTPException(status_code=400, detail="Invalid image data")
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

def generate_viewer_html_with_data(data):
    """Generate self-contained viewer HTML with embedded data"""
    mode = data.get("mode", "single")
    use_pics = data.get("use_pics", False)
    placements = data.get("placements", [])
    road_image = data.get("road_image", "")
    artwork_urls = data.get("artwork_urls", {})
    
    header_title = "Two Way" if mode == "two" else "Single Way"
    
    # Load template
    viewer_template_path = TEMPLATES_DIR / "viewer.html"
    if viewer_template_path.exists():
        with open(viewer_template_path, "r", encoding="utf-8") as f:
            template = f.read()
        
        # Replace placeholders
        html = template.replace("{{HEADER_TITLE}}", header_title)
        html = html.replace("{{ROAD_IMAGE}}", road_image)
        html = html.replace("{{MODE}}", mode)
        html = html.replace("{{USE_PICS}}", str(use_pics).lower())
        html = html.replace("{{PLACEMENTS_JSON}}", json.dumps(placements))
        html = html.replace("{{ARTWORK_URLS_JSON}}", json.dumps(artwork_urls))
        
        return html
    else:
        # Fallback to inline HTML if template not found
        logger.warning("Viewer template not found, using inline HTML")
        return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Artwork Sequence Viewer</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root{{
      --bg: #0f172a;
      --panel: rgba(255,255,255,0.03);
      --border: rgba(255,255,255,0.08);
      --text: #e2e8f0;
      --muted: #94a3b8;
    }}
    html, body {{ height: 100%; margin: 0; font-family: Inter, system-ui, -apple-system, sans-serif; background: radial-gradient(1400px 700px at 10% -10%, #0b1220 0%, #0f172a 60%, #0a0f1f 100%); color: var(--text); }}
    #viewer {{ display: flex; flex-direction: column; height: 100vh; }}
    header {{ padding: 14px 16px; backdrop-filter: blur(8px); background: linear-gradient(180deg, rgba(2,6,23,0.75), rgba(2,6,23,0.55)); border-bottom: 1px solid var(--border); }}
    header h2 {{ margin: 0; font-size: 18px; letter-spacing: .2px; font-weight: 700; text-align: center; }}
    #main {{ flex: 1; position: relative; display:flex; align-items:center; justify-content:center; padding: 12px; }}
    #stage {{ position: relative; width: 100%; height: 100%; border-radius: 16px; overflow: hidden; border: 1px solid var(--border); box-shadow: 0 12px 50px rgba(2,6,23,0.45); background: #0b1220; }}
    #img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
    #markers {{ position:absolute; left:0; top:0; width:100%; height:100%; pointer-events:none; }}
    .marker {{ position:absolute; border:2px solid #000; background:#fff; width:14px; height:28px; display:flex; flex-direction: column; border-radius: 3px; box-shadow: 0 3px 12px rgba(0,0,0,0.35); pointer-events:auto; }}
    .marker .sq {{ flex:1; border-bottom:1px solid #000; display:flex; align-items:center; justify-content:center; font-weight:700; font-size: 9px; color:#fff; cursor: pointer; }}
    .marker .sq:last-child {{ border-bottom:0; }}
    .marker .sq.side1 {{ border-color:#0033AA; background:#0066FF; }}
    .marker .sq.side2 {{ border-color:#AA0000; background:#FF3333; }}
    #preview {{ position:absolute; display:none; border: 3px solid #fff; background:rgba(15,23,42,0.9); box-shadow: 0 8px 32px rgba(0,0,0,0.8), 0 0 0 1px rgba(0,0,0,0.5); padding:8px; border-radius: 12px; z-index:9999; pointer-events: none; }}
    #preview img {{ max-width:min(35vw,400px); max-height:min(35vh,400px); object-fit:contain; border:0; border-radius: 8px; display:block; }}
  </style>
</head>
<body>
  <div id="viewer">
    <header>
      <h2>Artwork Sequence - {header_title} Road</h2>
    </header>
    <div id="main">
      <div id="stage">
        <img id="img" src="{road_image}" />
        <div id="markers"></div>
        <div id="preview"><img id="prevImg" /></div>
      </div>
    </div>
  </div>
  <script>
    const MODE = '{mode}';
    const USE_PICS = {str(use_pics).lower()};
    const placements = {json.dumps(placements)};
    const artworkUrls = {json.dumps(artwork_urls)};
    const markerW = 14, markerH = 28;
    
    const imgEl = document.getElementById('img');
    const markersEl = document.getElementById('markers');
    const previewEl = document.getElementById('preview');
    const prevImg = document.getElementById('prevImg');
    
    function getDrawInfo() {{
      const elW = imgEl.clientWidth, elH = imgEl.clientHeight;
      const iw = imgEl.naturalWidth, ih = imgEl.naturalHeight;
      const scale = Math.min(elW/iw, elH/ih);
      const drawW = iw*scale, drawH = ih*scale;
      const offX = (elW - drawW)/2;
      const offY = (elH - drawH)/2;
      return {{ elW, elH, iw, ih, scale, drawW, drawH, offX, offY }};
    }}
    
    function px(x) {{
      const info = getDrawInfo();
      return info.offX + x*info.scale;
    }}
    
    function py(y) {{
      const info = getDrawInfo();
      return info.offY + y*info.scale;
    }}
    
    function redraw() {{
      markersEl.innerHTML = '';
      for (const p of placements) {{
        const m = document.createElement('div');
        m.className = 'marker';
        m.style.left = (px(p.x) - markerW/2) + 'px';
        m.style.top = (py(p.y) - markerH/2) + 'px';
        
        const s1 = document.createElement('div');
        s1.className = 'sq side1';
        s1.textContent = (p.s1_num || p.s1_icon || '');
        
        const s2 = document.createElement('div');
        s2.className = 'sq side2';
        if (MODE === 'two') {{
          s2.textContent = (p.s2_num || p.s2_icon || '');
        }}
        
        m.appendChild(s1);
        if (MODE === 'two') m.appendChild(s2);
        
        // Hover preview for pictures
        if (USE_PICS) {{
          s1.onmouseenter = (e) => showPreview(e, p.s1_icon, p.x);
          s1.onmouseleave = () => hidePreview();
          if (MODE === 'two') {{
            s2.onmouseenter = (e) => showPreview(e, p.s2_icon, p.x);
            s2.onmouseleave = () => hidePreview();
          }}
        }}
        
        markersEl.appendChild(m);
      }}
    }}
    
    function showPreview(e, iconId, imgX) {{
      if (!iconId || !artworkUrls[iconId]) {{
        hidePreview();
        return;
      }}
      prevImg.src = artworkUrls[iconId];
      previewEl.style.display = 'block';
      
      // Position preview
      setTimeout(() => {{
        const info = getDrawInfo();
        const roadImage = imgEl;
        const placeRight = imgX < (roadImage.naturalWidth/2);
        
        const imgW = previewEl.offsetWidth || 400;
        const imgH = previewEl.offsetHeight || 400;
        const margin = 20;
        
        let x, y;
        
        if (placeRight) {{
          x = info.offX + info.drawW - imgW - margin;
        }} else {{
          x = info.offX + margin;
        }}
        
        y = info.offY + (info.drawH - imgH) / 2;
        
        x = Math.max(info.offX + margin, Math.min(x, info.offX + info.drawW - imgW - margin));
        y = Math.max(info.offY + margin, Math.min(y, info.offY + info.drawH - imgH - margin));
        
        previewEl.style.left = x + 'px';
        previewEl.style.top = y + 'px';
      }}, 10);
    }}
    
    function hidePreview() {{
      previewEl.style.display = 'none';
    }}
    
    window.addEventListener('resize', redraw);
    imgEl.onload = redraw;
    redraw();
  </script>
</body>
</html>"""

# Cleanup functions
async def cleanup_old_data():
    """Remove data older than retention period"""
    try:
        current_time = datetime.now()
        retention_threshold = current_time - timedelta(days=DATA_RETENTION_DAYS)
        
        # Cleanup viewers
        viewers_to_remove = []
        for viewer_id, viewer_data in viewers.items():
            created_at = datetime.fromisoformat(viewer_data.get("created_at", current_time.isoformat()))
            if created_at < retention_threshold:
                viewers_to_remove.append(viewer_id)
        
        for viewer_id in viewers_to_remove:
            # Delete file from disk
            viewer_metadata = viewers.get(viewer_id, {})
            if "file_path" in viewer_metadata:
                file_path = Path(viewer_metadata["file_path"])
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted viewer file: {file_path.name}")
            del viewers[viewer_id]
        
        # Cleanup results
        results_to_remove = []
        for result_id, result_data in results.items():
            created_at = datetime.fromisoformat(result_data.get("created_at", current_time.isoformat()))
            if created_at < retention_threshold:
                results_to_remove.append(result_id)
        
        for result_id in results_to_remove:
            del results[result_id]
        
        if viewers_to_remove or results_to_remove:
            logger.info(f"Cleaned up {len(viewers_to_remove)} viewers and {len(results_to_remove)} results older than {DATA_RETENTION_DAYS} days")
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

async def enforce_storage_limits():
    """Enforce maximum storage limits to prevent memory issues"""
    try:
        # Check viewers limit
        if len(viewers) > MAX_STORAGE_ITEMS:
            # Sort by creation date and remove oldest
            sorted_viewers = sorted(
                viewers.items(), 
                key=lambda x: x[1].get("created_at", ""),
                reverse=True
            )
            viewers.clear()
            viewers.update(dict(sorted_viewers[:MAX_STORAGE_ITEMS]))
            logger.warning(f"Enforced viewer storage limit, removed {len(sorted_viewers) - MAX_STORAGE_ITEMS} items")
        
        # Check results limit
        if len(results) > MAX_STORAGE_ITEMS:
            sorted_results = sorted(
                results.items(),
                key=lambda x: x[1].get("created_at", ""),
                reverse=True
            )
            results.clear()
            results.update(dict(sorted_results[:MAX_STORAGE_ITEMS]))
            logger.warning(f"Enforced results storage limit, removed {len(sorted_results) - MAX_STORAGE_ITEMS} items")
    
    except Exception as e:
        logger.error(f"Error enforcing storage limits: {e}")

async def periodic_cleanup():
    """Run cleanup tasks periodically"""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_HOURS * 3600)  # Convert hours to seconds
        logger.info("Running periodic cleanup...")
        await cleanup_old_data()
        await enforce_storage_limits()

@app.on_event("startup")
async def startup_event():
    """Start background cleanup task on server startup"""
    asyncio.create_task(periodic_cleanup())
    logger.info(f"Server started with {DATA_RETENTION_DAYS}-day retention policy")

@app.get("/api/cleanup-stats")
async def get_cleanup_stats():
    """Get cleanup statistics and storage info"""
    current_time = datetime.now()
    
    # Calculate age statistics
    viewer_ages = []
    for viewer_data in viewers.values():
        created_at = datetime.fromisoformat(viewer_data.get("created_at", current_time.isoformat()))
        age_days = (current_time - created_at).days
        viewer_ages.append(age_days)
    
    result_ages = []
    for result_data in results.values():
        created_at = datetime.fromisoformat(result_data.get("created_at", current_time.isoformat()))
        age_days = (current_time - created_at).days
        result_ages.append(age_days)
    
    return {
        "current_viewers": len(viewers),
        "current_results": len(results),
        "oldest_viewer_days": max(viewer_ages, default=0),
        "oldest_result_days": max(result_ages, default=0),
        "retention_policy_days": DATA_RETENTION_DAYS,
        "max_storage_items": MAX_STORAGE_ITEMS,
        "next_cleanup_hours": CLEANUP_INTERVAL_HOURS
    }

@app.post("/api/manual-cleanup")
async def manual_cleanup(background_tasks: BackgroundTasks):
    """Trigger manual cleanup"""
    background_tasks.add_task(cleanup_old_data)
    background_tasks.add_task(enforce_storage_limits)
    return {"status": "cleanup initiated"}

# To run locally:
#   uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# For Render deployment, it will use PORT environment variable automatically