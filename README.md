# SpacetimeDB Project - Full Structure

Below is the complete project structure for the SpacetimeDB application with a Python Quart frontend and Rust server module:

```
spacetimedb-project/
├── docker-compose.yml             # Main Docker Compose configuration
│
├── server/                        # Rust server module
│   ├── Dockerfile                 # Server container configuration 
│   ├── Cargo.toml                 # Rust dependencies (fixed)
│   └── src/
│       └── lib.rs                 # Server game logic (fixed)
│
└── client/                        # Python Quart application
    ├── Dockerfile                 # Client container configuration
    ├── app.py                     # Main Quart application
    ├── requirements.txt           # Python dependencies
    ├── templates/
    │   └── index.html             # Main page template with Three.js
    ├── static/
    │   └── main.css               # CSS styles
    └── models/                    # Directory for 3D model files
        └── .gitkeep               # Placeholder to ensure directory is created
```

## Key Components:

### Docker Compose (docker-compose.yml)
Orchestrates three containers:
- SpacetimeDB
- Rust server module
- Python Quart application

### Rust Server Module (server/)
Contains the game logic written in Rust with the correct SpacetimeDB API:
- Uses fully qualified paths for spacetimedb macros (`#[spacetimedb::table]`, etc.)
- Handles Timestamp serialization properly with `unix_timestamp_millis()`
- Uses proper function calls instead of macros for database operations
- Manages game entities and their positions
- Provides reducers for creating and updating entities
- Exposes queries for retrieving entity data

### Python Quart Application (client/)
Handles the web frontend and acts as intermediary:
- Serves HTML/CSS/JavaScript with Three.js for 3D visualization
- Maintains WebSocket connections to browsers
- Connects to SpacetimeDB via WebSocket API
- Forwards entity updates in real-time

### No TypeScript Required
- Three.js is loaded directly from CDN
- JavaScript is embedded in the HTML template
- No build/compilation step needed for frontend