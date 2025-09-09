# Artwork Sequencer Application

A web-based application for placing and tracking artwork positions on road images. The application supports both single-way and two-way roads, with options for using numbered markers or actual artwork images.

## Architecture Overview

The application is architected with a clear separation between frontend and backend:

- **Frontend**: Pure HTML/CSS/JavaScript client (web_sequencer.html)
- **Backend**: FastAPI server providing REST APIs (server.py)
- **Communication**: All frontend-backend communication happens via REST APIs

## Features

- Upload road images (PNG, JPG, or PDF) and optionally artwork images
- Automatic PDF to image conversion (first page)
- Place blue/red markers on the road image
- Support for single-way and two-way roads
- Number mode: Edit numbers inline for each marker
- Picture mode: Select from uploaded artwork images
- Drag and drop repositioning of markers
- Generate shareable client view with untraceable URLs
- Export final image with markers and detailed report

## Project Structure

```
/Users/amr/Documents/Pixel Finder/
├── server.py              # Backend FastAPI server
├── web_sequencer.html     # Frontend application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Backend API Documentation

### Core Endpoints

#### `GET /`
Landing page with project overview.

#### `GET /app`
Serves the main editor application.

#### `GET /health`
Health check endpoint returning server status and counters.

### API Endpoints

#### `POST /api/create-viewer`
Creates a shareable viewer link with untraceable UUID.

**Request Body:**
```json
{
  "mode": "single|two",
  "use_pics": boolean,
  "placements": [...],
  "road_image": "data:image/png;base64,...",
  "artwork_urls": {...},
  "base_url": "http://localhost:8000"
}
```

**Response:**
```json
{
  "viewer_id": "uuid-string",
  "url": "/viewer/{viewer_id}",
  "full_url": "http://localhost:8000/viewer/{viewer_id}"
}
```

#### `GET /viewer/{viewer_id}`
Serves the viewer page for a specific ID.

#### `GET /api/viewer/{viewer_id}/data`
Returns the viewer data (placements, images, etc.).

#### `POST /api/save-result`
Saves result data (image and report) and returns ID for retrieval.

#### `POST /api/generate-report`
Generates a detailed report from placement data.

**Request Body:**
```json
{
  "mode": "single|two",
  "use_pics": boolean,
  "num_arts": 8,
  "placements": [...]
}
```

## Frontend Guide

### Key Components

1. **State Management**
   - All state is managed in JavaScript variables
   - No direct database access
   - Communication with backend only through APIs

2. **Image Processing**
   - Images are converted to data URLs for API transmission
   - Canvas API used for final image generation
   - All processing happens client-side

3. **User Interface**
   - Three-panel layout: Instructions (left), Canvas (center), Options (right)
   - Responsive design that adapts to smaller screens
   - Dark theme with modern glassmorphism effects

### Modifying the Frontend

#### Adding New Features

1. **UI Elements**: Add to the HTML structure in web_sequencer.html
2. **Styling**: Update the CSS in the `<style>` section
3. **Logic**: Add JavaScript functions in the `<script>` section

#### Key Functions to Know

- `onStageClick(e)`: Handles clicks on the canvas to place markers
- `redraw()`: Redraws all markers on the canvas
- `processResults()`: Generates final image and calls backend APIs
- `buildChoices()`: Populates artwork selection panel

#### API Integration Pattern

```javascript
// Example of calling backend API
const response = await fetch(`${API_BASE_URL}/api/endpoint`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: ... })
});
const result = await response.json();
```

### Data Flow

1. User uploads road image → Stored as blob/data URL in frontend
2. User places markers → Stored in `placements` array
3. User clicks Done → Frontend generates image and calls APIs
4. Backend creates viewer ID → Returns untraceable URL
5. Client view fetches data → Backend serves viewer data

## Running the Application

### Prerequisites

- Python 3.8+
- Node.js (optional, for development tools)

### Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Open browser to `http://localhost:8000`

## Security Considerations

- Viewer URLs use UUIDs that cannot be traced back to the edit session
- No authentication implemented (add if needed)
- CORS is currently open (`allow_origins=["*"]`) - restrict in production
- In-memory storage - use database for production

## Data Cleanup Strategy

The server implements a comprehensive 30-day data retention and cleanup strategy:

### Automatic Cleanup Features

1. **30-Day Retention Policy**
   - All viewer and result data is automatically deleted after 30 days
   - Configurable via `DATA_RETENTION_DAYS` variable

2. **Storage Limits**
   - Maximum 10,000 items stored (configurable via `MAX_STORAGE_ITEMS`)
   - Oldest items removed when limit is exceeded

3. **Periodic Cleanup**
   - Runs every 24 hours automatically
   - Removes expired data and enforces storage limits
   - Logs all cleanup activities

### API Endpoints for Monitoring

#### `GET /api/cleanup-stats`
View current storage statistics and cleanup information:
```json
{
  "current_viewers": 150,
  "current_results": 200,
  "oldest_viewer_days": 25,
  "oldest_result_days": 28,
  "retention_policy_days": 30,
  "max_storage_items": 10000,
  "next_cleanup_hours": 24
}
```

#### `POST /api/manual-cleanup`
Trigger manual cleanup immediately (useful for maintenance).

### Configuration

Adjust these variables in `server.py`:
```python
CLEANUP_INTERVAL_HOURS = 24  # How often to run cleanup
DATA_RETENTION_DAYS = 30     # How long to keep data
MAX_STORAGE_ITEMS = 10000    # Maximum items to store
```

### Storage Implementation

The application uses disk-based storage for viewer HTML files:
- Viewer HTML files are stored in `/data/` directory
- Each viewer gets a unique file: `viewer_{uuid}.html`
- Files are self-contained with all data embedded
- Metadata is kept in memory for fast access

On Render deployment:
- A 1GB persistent disk is mounted at `/data`
- Files persist across deployments and restarts
- Automatic cleanup removes files older than 30 days

### Production Recommendations

For larger scale deployments, consider:
1. **Database Storage**: Replace in-memory metadata with PostgreSQL/MongoDB
2. **S3/Blob Storage**: Store HTML files in cloud storage for better scalability
3. **CDN**: Serve viewer files through a CDN for global access
4. **Monitoring**: Set up alerts for disk usage and cleanup failures
5. **Archival**: Archive old data instead of deleting if needed for compliance

## Deployment

For production deployment:

1. Use a proper database instead of in-memory storage
2. Add authentication/authorization
3. Configure CORS appropriately
4. Use environment variables for configuration
5. Add proper logging and monitoring
6. Consider using a CDN for static assets
7. Implement rate limiting

## Frontend Development Tips

### State Variables
- `MODE`: 'single' or 'two' (road type)
- `USE_PICS`: boolean (pictures vs numbers)
- `placements`: array of marker positions and values
- `artworks`: array of uploaded artwork images

### Event Handlers
- Mode changes: Radio buttons update `MODE`
- Picture mode: Checkbox updates `USE_PICS`
- File uploads: Handled by `onchange` events
- Canvas clicks: Managed by `onStageClick`

### Styling
- CSS variables in `:root` for easy theming
- Responsive grid layout
- Dark theme with transparency effects
- Consistent border radius and shadows

### Best Practices
1. Always convert images to data URLs before API calls
2. Use `async/await` for API calls
3. Update UI state after successful API responses
4. Show status messages for user feedback
5. Validate inputs before API calls

## Troubleshooting

### Common Issues

1. **Images not loading**: Check CORS settings and ensure proper data URL conversion
2. **API errors**: Check server logs and browser console
3. **Viewer not working**: Ensure viewer ID exists in backend storage
4. **Export failing**: Check canvas rendering and data URL generation

### Debug Mode

Add console.log statements in key functions:
- `processResults()`: Log API responses
- `onStageClick()`: Log click coordinates
- `redraw()`: Log placement data

## Future Enhancements

1. Add persistent storage (PostgreSQL/MongoDB)
2. Implement user accounts and projects
3. Add undo/redo functionality
4. Support for different marker shapes/sizes
5. Batch operations for markers
6. Export to different formats (SVG, PDF)
7. Real-time collaboration features
8. Mobile app version