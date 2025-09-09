# Artwork Sequencer Application

A web-based application for placing and tracking artwork positions on road images. Supports both single-way and two-way roads with numbered markers or actual artwork images.

## 📁 Project Structure

```
/
├── templates/                # All frontend HTML files
│   ├── web_sequencer.html   # Main editor application
│   ├── landing.html         # Landing page
│   └── viewer.html          # Client viewer template
├── data/                    # Viewer storage (auto-created)
├── server.py                # Backend API server
├── requirements.txt         # Python dependencies
├── render.yaml             # Deployment configuration
└── README.md               # This file
```

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Open the app**: http://localhost:8000

## ✨ Features

- **Upload Support**: PNG, JPG, or PDF road images
- **Two Modes**: Single-way or two-way roads
- **Marker Types**: Numbers or picture mode with artwork images
- **Interactive Editing**: Click to place, drag to reposition markers
- **Client View**: Generate shareable viewer links with untraceable URLs
- **Export Options**: Download final image and detailed report
- **Auto-cleanup**: 30-day retention policy for stored viewers

---

# 🎨 Comprehensive Frontend Developer Guide

## Overview

The frontend consists of three main HTML files in the `templates/` directory. Each file is self-contained with its own HTML, CSS, and JavaScript. No build process is required - just edit and refresh!

## Frontend Architecture

### 1. Landing Page (`templates/landing.html`)

**Purpose**: Entry point and marketing page

**Key Elements**:
- Hero section with app title and description
- Feature cards explaining functionality
- Call-to-action buttons
- Responsive grid layout

**Customization Points**:
```html
<!-- Logo customization -->
<div class="logo"></div>  <!-- Line 22 - Add your logo here -->

<!-- Main CTA button -->
<a class="btn" href="/app">Open Editor</a>  <!-- Line 60 -->

<!-- Color scheme variables -->
:root{
  --bg: #0f172a;        /* Background color */
  --panel: #0b1220;     /* Panel background */
  --text: #e2e8f0;      /* Text color */
  --btn: #22c55e;       /* Button color */
  --accent: #38bdf8;    /* Accent color */
}
```

### 2. Main Editor (`templates/web_sequencer.html`)

**Purpose**: Core application for placing markers on road images

#### HTML Structure
```html
<!-- Page Layout -->
<header>                    <!-- Top toolbar -->
  <h1>Artwork Sequencer</h1>
  <div id="tools">          <!-- Mode toggles and controls -->
    <button id="btnSingle">Single Way</button>
    <button id="btnTwo">Two Way</button>
    <button id="btnNums">Numbers</button>
    <button id="btnPics">Pictures</button>
  </div>
</header>

<div id="left">             <!-- Left panel: Instructions -->
  <h3>How to use</h3>
  <ol id="tips">...</ol>
</div>

<div id="main">             <!-- Center: Canvas area -->
  <div id="status">...</div>
  <input type="file" id="file" />
  <div id="stage">
    <img id="img" />        <!-- Road image -->
    <div id="markers">...</div>  <!-- Marker overlays -->
    <div id="preview">...</div>  <!-- Hover preview -->
  </div>
</div>

<div id="right">            <!-- Right panel: Artwork selector -->
  <h3>Artworks</h3>
  <input type="file" id="artFiles" multiple />
  <div id="artworkGrid">...</div>
</div>

<footer>                    <!-- Bottom: Action buttons -->
  <button id="btnClear">Clear All</button>
  <button id="btnDone">Done</button>
</footer>
```

#### JavaScript Variables & State

```javascript
// Application State
let MODE = 'single';        // Current mode: 'single' or 'two'
let USE_PICS = false;       // true for pictures, false for numbers
let SELECTED_ART = null;    // Currently selected artwork ID
let roadImage = null;       // Uploaded road image File object
let artworks = [];          // Array of uploaded artwork Files
let placements = [];        // Array of placed markers

// Placement Object Structure
{
  x: 100,           // X coordinate on original image
  y: 200,           // Y coordinate on original image
  s1_num: "1",      // Side 1 number (numbers mode)
  s1_icon: "art1",  // Side 1 artwork ID (pictures mode)
  s2_num: "2",      // Side 2 number (for two-way mode)
  s2_icon: "art2"   // Side 2 artwork ID (for two-way mode)
}

// UI Constants
const markerW = 20;         // Marker width in pixels
const markerH = 40;         // Marker height in pixels
```

#### Key Functions Reference

```javascript
// Image Upload & Processing
async function handleFileChange(e) {
  // Handles road image upload
  // Converts PDF to image if needed
  // Sets up canvas for editing
}

async function pdfToImage(file) {
  // Converts PDF first page to PNG
  // Uses pdf.js library
  // Returns canvas with rendered PDF
}

// Canvas Interaction
function onStageClick(e) {
  // Handles clicks on the road image
  // Places new markers at click position
  // Manages edit mode for existing markers
}

function redraw() {
  // Renders all markers on canvas
  // Updates marker positions
  // Handles drag & drop visual feedback
}

// Coordinate System
function getDrawInfo() {
  // Calculates image scaling and positioning
  // Returns object with transformation data
  return {
    elW, elH,       // Element dimensions
    iw, ih,         // Image natural dimensions
    scale,          // Current scale factor
    drawW, drawH,   // Drawn dimensions
    offX, offY      // Offset for centering
  };
}

function toImgCoords(clientX, clientY) {
  // Converts browser coordinates to image coordinates
  // Accounts for image scaling and centering
}

// Marker Management
function createEditDialog(p, isNew) {
  // Creates inline edit UI for markers
  // Handles number input in numbers mode
  // Returns dialog element
}

function makeDraggable(element, placement) {
  // Makes marker draggable
  // Updates placement coordinates on drag
  // Calls redraw() on position change
}

// Export Functions
async function processResults() {
  // Generates final output image
  // Creates report text
  // Prepares download data
}

async function generateImage() {
  // Renders final image with markers
  // Uses original image dimensions
  // Returns base64 PNG data
}

// API Integration
async function createViewer() {
  // POST to /api/create-viewer
  // Sends current state to backend
  // Returns viewer URL
}

async function generateReport() {
  // POST to /api/generate-report
  // Sends placement data
  // Returns formatted report text
}
```

#### Styling Customization

```css
/* Color Scheme */
:root {
  --bg: #f8fafc;          /* Background */
  --panel: #ffffff;        /* Panel background */
  --border: #e2e8f0;       /* Border color */
  --text: #1e293b;         /* Text color */
  --muted: #64748b;        /* Muted text */
  --accent: #3b82f6;       /* Accent color */
  --hover: #dbeafe;        /* Hover state */
}

/* Dark Mode (add class="dark" to body) */
body.dark {
  --bg: #0f172a;
  --panel: #1e293b;
  --border: #334155;
  --text: #f1f5f9;
  --muted: #94a3b8;
  --accent: #60a5fa;
  --hover: #1e40af;
}

/* Marker Styles */
.marker {
  /* Customize marker appearance */
  border-radius: 4px;      /* Rounded corners */
  box-shadow: ...;         /* Drop shadow */
}

.marker .sq.side1 {
  background: #0066FF;     /* Blue side color */
}

.marker .sq.side2 {
  background: #FF3333;     /* Red side color */
}
```

### 3. Client Viewer (`templates/viewer.html`)

**Purpose**: Read-only viewer for shared links

**Template Variables**:
- `{{HEADER_TITLE}}` - Display title ("Single Way" or "Two Way")
- `{{ROAD_IMAGE}}` - Base64 encoded road image
- `{{MODE}}` - Mode string ('single' or 'two')
- `{{USE_PICS}}` - Boolean for pictures mode
- `{{PLACEMENTS_JSON}}` - JSON array of placements
- `{{ARTWORK_URLS_JSON}}` - JSON object mapping artwork IDs to URLs

**Key Functions**:
```javascript
function redraw() {
  // Renders all markers in view-only mode
  // No editing capabilities
}

function showPreview(e, iconId, imgX) {
  // Shows artwork preview on hover
  // Positions preview based on marker location
}
```

## Common Frontend Tasks

### 1. Adding a Dark Mode Toggle

```javascript
// In web_sequencer.html, add to header:
<button id="btnTheme">🌙</button>

// Add JavaScript:
document.getElementById('btnTheme').onclick = () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
};

// Load theme on startup:
if (localStorage.getItem('theme') === 'dark') {
  document.body.classList.add('dark');
}
```

### 2. Adding Keyboard Shortcuts

```javascript
// Add to web_sequencer.html:
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey) {
    switch(e.key) {
      case 'z': undo(); break;
      case 'y': redo(); break;
      case 's': e.preventDefault(); saveDraft(); break;
    }
  }
});
```

### 3. Adding Loading Animations

```javascript
// Add loading spinner function:
function showLoading(message) {
  const loader = document.createElement('div');
  loader.className = 'loader';
  loader.innerHTML = `
    <div class="spinner"></div>
    <p>${message}</p>
  `;
  document.body.appendChild(loader);
}

// CSS for spinner:
.loader {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.spinner {
  width: 40px; height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### 4. Adding Tooltips

```javascript
// Add tooltip on hover:
marker.title = `Position: ${p.x}, ${p.y}`;

// Or create custom tooltip:
function showTooltip(element, text) {
  const tooltip = document.createElement('div');
  tooltip.className = 'tooltip';
  tooltip.textContent = text;
  
  const rect = element.getBoundingClientRect();
  tooltip.style.left = rect.left + 'px';
  tooltip.style.top = (rect.top - 30) + 'px';
  
  document.body.appendChild(tooltip);
  
  element.addEventListener('mouseleave', () => {
    tooltip.remove();
  });
}
```

### 5. Mobile Responsiveness

```css
/* Add media queries to web_sequencer.html */
@media (max-width: 768px) {
  body { flex-direction: column; }
  #left, #right { 
    width: 100%; 
    max-width: none;
    order: 2;
  }
  #main { 
    order: 1;
    height: 50vh;
  }
  header { 
    flex-wrap: wrap;
    gap: 8px;
  }
  #tools button {
    flex: 1;
    min-width: 80px;
  }
}
```

### 6. Adding Export Options

```javascript
// Add new export format:
function exportAsJSON() {
  const data = {
    version: "1.0",
    mode: MODE,
    placements: placements,
    metadata: {
      created: new Date().toISOString(),
      totalMarkers: placements.length
    }
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'artwork_placements.json';
  a.click();
}
```

## API Integration Guide

### Making API Calls

```javascript
// Generic API call function
async function apiCall(endpoint, data = null) {
  try {
    const options = {
      method: data ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(endpoint, options);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    alert('Operation failed. Please try again.');
    throw error;
  }
}

// Example usage:
const viewerData = await apiCall('/api/create-viewer', {
  mode: MODE,
  use_pics: USE_PICS,
  placements: placements,
  road_image: roadImageData,
  artwork_urls: artworkUrls
});
```

### Available Endpoints

1. **Create Viewer**: `POST /api/create-viewer`
   - Creates shareable read-only viewer
   - Returns unique viewer URL

2. **Generate Report**: `POST /api/generate-report`
   - Creates text report of artwork requirements
   - Returns formatted report string

3. **Health Check**: `GET /health`
   - Returns server status
   - Shows viewer and result counts

4. **Cleanup Stats**: `GET /api/cleanup-stats`
   - Shows storage statistics
   - Displays retention information

## CSS Architecture

### Layout System
```css
/* Flexbox-based layout */
body {
  display: flex;
  height: 100vh;
}

#left, #right {
  width: 260px;
  flex-shrink: 0;
}

#main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

#stage {
  flex: 1;
  position: relative;
}
```

### Component Styling
```css
/* Button styles */
button {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--panel);
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s;
}

button:hover {
  background: var(--hover);
  transform: translateY(-1px);
}

button.active {
  background: var(--accent);
  color: white;
}

/* Panel styles */
.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}
```

## Performance Optimization

### Image Handling
```javascript
// Optimize large images
function resizeImage(file, maxWidth, maxHeight) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      let width = img.width;
      let height = img.height;
      
      if (width > height) {
        if (width > maxWidth) {
          height *= maxWidth / width;
          width = maxWidth;
        }
      } else {
        if (height > maxHeight) {
          width *= maxHeight / height;
          height = maxHeight;
        }
      }
      
      canvas.width = width;
      canvas.height = height;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, width, height);
      
      canvas.toBlob(resolve, 'image/jpeg', 0.9);
    };
    img.src = URL.createObjectURL(file);
  });
}
```

### Debouncing
```javascript
// Debounce function for performance
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Usage:
const debouncedRedraw = debounce(redraw, 16);
window.addEventListener('resize', debouncedRedraw);
```

## Testing & Debugging

### Debug Mode
```javascript
// Add debug mode
const DEBUG = localStorage.getItem('debug') === 'true';

function log(...args) {
  if (DEBUG) console.log('[Artwork Sequencer]', ...args);
}

// Enable: localStorage.setItem('debug', 'true')
// Disable: localStorage.removeItem('debug')
```

### Error Handling
```javascript
// Global error handler
window.addEventListener('error', (e) => {
  console.error('Global error:', e);
  status('An error occurred. Please refresh and try again.', 'error');
});

// Promise rejection handler
window.addEventListener('unhandledrejection', (e) => {
  console.error('Unhandled promise rejection:', e);
  status('Operation failed. Please try again.', 'error');
});
```

## Browser Compatibility

### Required Features
- ES6+ JavaScript
- Canvas API
- FileReader API
- Fetch API
- CSS Grid/Flexbox

### Polyfills (if needed)
```html
<!-- Add to head for older browsers -->
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6,fetch"></script>
```

## Security Considerations

### Input Validation
```javascript
// Validate file uploads
function validateImageFile(file) {
  const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
  if (!validTypes.includes(file.type)) {
    throw new Error('Invalid file type. Please upload PNG, JPG, or PDF.');
  }
  
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    throw new Error('File too large. Maximum size is 10MB.');
  }
}
```

### XSS Prevention
```javascript
// Sanitize user input
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
```

---

## 🔧 Backend API Reference

### Core Endpoints

#### `POST /api/create-viewer`
Creates a shareable viewer with unique URL.
```json
Request: {
  "mode": "single|two",
  "use_pics": boolean,
  "placements": [...],
  "road_image": "data:image/...",
  "artwork_urls": {...}
}

Response: {
  "viewer_id": "uuid",
  "url": "/viewer/{uuid}"
}
```

#### `POST /api/generate-report`
Generates artwork requirements report.
```json
Request: {
  "mode": "single|two",
  "use_pics": boolean,
  "num_arts": 8,
  "placements": [...]
}

Response: {
  "report": "text report..."
}
```

### Storage & Cleanup

- **Viewer Storage**: HTML files saved to `/data/viewer_{uuid}.html`
- **Retention**: Automatic deletion after 30 days
- **Disk Mount**: 1GB persistent storage on Render
- **Cleanup**: Runs daily, removes expired files

### Monitoring Endpoints

- `GET /health` - Server status and counts
- `GET /api/cleanup-stats` - Storage statistics
- `POST /api/manual-cleanup` - Trigger cleanup

## 🚀 Deployment (Render)

The app is configured for Render deployment:

1. **Push to GitHub**
2. **Connect to Render**
3. **Auto-deploys** from `render.yaml`

Configuration:
- **Region**: Singapore
- **Plan**: Starter
- **Disk**: 1GB at `/data`
- **Auto-deploy**: Enabled

## 🔒 Security

- Viewer URLs use UUIDs (untraceable)
- No authentication (add if needed)
- CORS open for development
- 30-day auto-cleanup

## 📋 Environment Variables

- `DATA_DIR` - Storage path (default: `./data`, Render: `/data`)
- `PORT` - Server port (Render sets automatically)

## 🛠️ Development Workflow

### Frontend Development Process

1. **Setup**:
   - Run server: `uvicorn server:app --reload`
   - Open: http://localhost:8000/app
   - Edit files in `templates/`
   - Refresh browser to see changes

2. **Testing**:
   - Use browser DevTools (F12)
   - Check console for errors
   - Test responsive design
   - Verify API responses

3. **Debugging**:
   ```javascript
   // Add breakpoints
   debugger;
   
   // Log API calls
   console.log('API Request:', data);
   console.log('API Response:', response);
   ```

### Common Issues & Solutions

**Issue**: Changes not appearing
- **Solution**: Hard refresh (Ctrl+Shift+R)

**Issue**: CORS errors
- **Solution**: Ensure server is running on correct port

**Issue**: File upload fails
- **Solution**: Check file size and type validation

**Issue**: Markers not positioning correctly
- **Solution**: Verify coordinate transformation functions

## 📦 Dependencies

### Frontend (CDN)
- **pdf.js** - PDF to image conversion
- **Inter font** - UI typography

### Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server

## 🐛 Troubleshooting

**Images not loading**: Check browser console for CORS errors
**PDF conversion fails**: Verify pdf.js CDN is accessible
**Viewer not found**: Check if file exists in data/ directory
**Cleanup not running**: Check server logs for errors

## 🤝 Contributing

### Frontend Developers
1. Work in `templates/` folder
2. Follow existing code style
3. Test all browsers
4. Update this README for new features

### Code Style Guide
- Use 2-space indentation
- Use const/let, avoid var
- Use async/await over promises
- Add comments for complex logic
- Keep functions under 50 lines

## 📄 License

[Add your license here]

---

Built with ❤️ using FastAPI and vanilla JavaScript