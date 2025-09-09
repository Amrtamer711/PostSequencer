# Artwork Sequencer - Frontend Developer Guide

A web app for placing and tracking artwork positions on road images. This guide is for frontend developers who want to improve the UI.

## 🎨 For Frontend Developers - Start Here!

### The Frontend File
**You only need to edit ONE file**: `web_sequencer.html`

This file contains:
- All HTML structure
- All CSS styles (in the `<style>` tag)
- All JavaScript logic (in the `<script>` tag)
- PDF.js library for PDF support

### What You CAN Change (Frontend)
✅ **UI/UX Design**
- Colors, fonts, layouts, animations
- Button styles, hover effects
- Responsive design improvements
- Add new UI components

✅ **User Interactions**
- Improve drag & drop behavior
- Add keyboard shortcuts
- Better error messages
- Loading states and animations

✅ **Visual Features**
- Canvas drawing improvements
- Marker styles and sizes
- Preview image behaviors
- Grid/guide lines

### What You SHOULD NOT Change (Backend Calls)
❌ **API Endpoints** - These must stay exactly the same:
```javascript
// Creating a viewer - DON'T CHANGE
fetch(`${API_BASE_URL}/api/create-viewer`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    mode: MODE,
    use_pics: USE_PICS,
    placements: placements,
    road_image: roadDataUrl,
    artwork_urls: artworkUrls
  })
});

// Generating reports - DON'T CHANGE
fetch(`${API_BASE_URL}/api/generate-report`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    mode: MODE,
    use_pics: USE_PICS,
    num_arts: NUM_ARTS,
    placements: placements
  })
});
```

## 🚀 Quick Start

1. **Run the Backend** (don't worry about how it works):
   ```bash
   pip install -r requirements.txt
   uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open the App**: Go to `http://localhost:8000/app`

3. **Edit the Frontend**: Open `web_sequencer.html` in your editor

4. **See Changes**: Just refresh your browser!

## 📁 File Structure

```
/
├── web_sequencer.html   # ← YOU EDIT THIS (Frontend)
├── server.py           # ← DON'T TOUCH (Backend)
├── requirements.txt    # ← DON'T TOUCH (Backend)
└── data/              # ← DON'T TOUCH (Storage)
```

## 🎯 Key Frontend Concepts

### 1. Main UI Sections
```html
<!-- Header with controls -->
<header>...</header>

<!-- Left panel with instructions -->
<div id="left">...</div>

<!-- Center canvas area -->
<div id="main">
  <div id="stage">
    <img id="img" />         <!-- Road image -->
    <div id="markers"></div> <!-- Marker overlays -->
  </div>
</div>

<!-- Right panel with artwork choices -->
<div id="right">...</div>

<!-- Footer with action buttons -->
<footer>...</footer>
```

### 2. Key JavaScript Variables
```javascript
// Current state - you can read but don't change how they're set
let MODE = 'single';        // 'single' or 'two' way road
let USE_PICS = false;       // true = pictures, false = numbers
let placements = [];        // Array of placed markers
let roadImage = null;       // The uploaded road image
let artworks = [];          // Uploaded artwork images
```

### 3. Key Functions You Might Want to Improve

**Drawing markers on canvas:**
```javascript
function redraw() {
  // This draws all the markers
  // You can change marker styles here
}
```

**Handling clicks:**
```javascript
function onStageClick(e) {
  // When user clicks on road image
  // You can add visual feedback here
}
```

**Hover previews:**
```javascript
function showPreview(e, iconId, imgX) {
  // Shows artwork preview on hover
  // You can improve the preview positioning/style
}
```

## 💡 Frontend Improvement Ideas

### Easy Improvements
- Add loading spinners during API calls
- Improve mobile responsiveness
- Add tooltips for better user guidance
- Animate marker placement
- Add a dark/light theme toggle

### Medium Improvements
- Add undo/redo functionality (store history in array)
- Implement zoom in/out for the canvas
- Add ruler/measurement tools
- Keyboard shortcuts for common actions
- Better file upload UI with drag & drop

### Advanced Improvements
- Add a minimap for large images
- Implement marker grouping/selection
- Add alignment guides when dragging
- Create a better artwork palette UI
- Add export to different formats

## ⚠️ Important Notes

1. **Don't change API endpoints** - The backend expects specific data formats
2. **Keep the data structure** - The `placements` array format must stay the same
3. **Test PDF uploads** - Make sure PDF conversion still works
4. **Preserve the viewer generation** - The client view feature must keep working

## 🧪 Testing Your Changes

1. **Upload a road image** (PNG, JPG, or PDF)
2. **Click to place markers**
3. **Try both modes** (Single Way / Two Way)
4. **Test drag & drop**
5. **Click "Done" and verify**:
   - Client View opens correctly
   - Download Picture matches preview
   - Download Report has correct data

## 🚫 Backend (Don't Touch!)

The backend handles:
- Serving the web page
- Creating viewer links
- Generating reports
- Managing storage
- Cleaning old files

You don't need to understand it - just know it provides the API endpoints your frontend uses.

## 📞 Need Help?

If you need the backend changed:
1. Don't edit `server.py` yourself
2. Ask for the specific API change you need
3. Explain what data you need to send/receive

Remember: Focus on making the UI beautiful and user-friendly. The backend will handle the rest!

---

## For Backend Developers Only

<details>
<summary>Click to expand backend details</summary>

### Backend Architecture
- **Framework**: FastAPI with Python
- **Storage**: File-based HTML storage in `/data/`
- **Cleanup**: Automatic 30-day retention
- **Deployment**: Render.com with persistent disk

### API Endpoints
- `POST /api/create-viewer` - Creates viewer with HTML file
- `GET /viewer/{id}` - Serves viewer HTML from disk
- `POST /api/generate-report` - Generates text report
- `GET /api/cleanup-stats` - Monitor storage usage

### Environment Variables
- `DATA_DIR` - Storage directory (default: `./data`, Render: `/data`)
- `PORT` - Server port (Render sets automatically)

</details>