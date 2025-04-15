# SpacetimeDB Game with Three.js and Python

This repository contains a multiplayer game project built with SpacetimeDB, Python, and Three.js. The setup demonstrates how to create a real-time 3D environment where multiple clients can interact with shared game entities.

## Project Overview

The project consists of three main components:

1. **SpacetimeDB**: The database and server platform for real-time multiplayer games
2. **Rust Server Module**: The game logic written in Rust
3. **Python Quart Client**: The web application serving the Three.js frontend

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│   SpacetimeDB   │◄────────┤  Rust Module    │◄────────┤  Python Client  │◄───── Web Browsers
│   (Database)    │         │  (Game Logic)   │         │  (Web Server)   │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

- **SpacetimeDB** handles data storage and synchronization
- **Rust Module** defines game entities and logic
- **Python Client** serves the web interface and connects to SpacetimeDB

## Directory Structure

```
spacetimedb-project/
├── docker-compose.yml             # Docker Compose configuration
│
├── server/                        # Rust server module
│   ├── Dockerfile                 # Server container configuration 
│   ├── Cargo.toml                 # Rust dependencies
│   └── src/
│       └── lib.rs                 # Server game logic
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
        └── .gitkeep               # Placeholder
```

## Features

- **Real-time 3D Environment**: Built with Three.js
- **Entity Creation and Manipulation**: Create and update 3D objects
- **Multiplayer Support**: Changes are synchronized across all clients
- **Persistent Game State**: Entities persist in the SpacetimeDB database
- **Responsive UI**: With connection status and entity information
- **3D Model Support**: Load custom 3D models (.obj, .fbx, etc.)

## Technologies Used

- **SpacetimeDB**: For multiplayer state synchronization
- **Rust**: For reliable server-side game logic
- **Python**: For the web server and SpacetimeDB client
- **Quart**: Asynchronous web framework for Python
- **Three.js**: JavaScript 3D library
- **Docker**: For containerization and deployment

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/spacetimedb-game.git
   cd spacetimedb-game
   ```

2. Start the containers:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Web interface: http://localhost:8080
   - SpacetimeDB interface: http://localhost:3000

### Controls

- Press "C" or click the "Create Entity" button to create a new random entity
- Use mouse to orbit the camera around the scene
- Entity information is displayed in the top-right panel

## Development

### Rust Server Module

The Rust module defines the game entities and logic:

```rust
#[spacetimedb::table]
#[derive(Clone, Debug, PartialEq, SpacetimeType)]
pub struct GameEntity {
    #[spacetimedb::primarykey]
    pub id: u64,
    pub position_x: f32,
    pub position_y: f32,
    pub position_z: f32,
    pub owner: Identity,
    pub created_at: Timestamp,
}
```

Reducers handle entity creation and updates:

```rust
#[spacetimedb::reducer]
pub fn create_entity(ctx: ReducerContext, position_x: f32, position_y: f32, position_z: f32) -> u64 {
    // Create an entity...
}
```

### Python Client

The Python client uses the `spacetimedb-sdk` to connect to SpacetimeDB:

```python
client = SpacetimeDBClient()
await client.connect(spacetime_url, MODULE_NAME)
client.subscribe_table("GameEntity", on_entity_update)
```

### Three.js Frontend

The Three.js frontend visualizes the entities in 3D space:

```javascript
function createEntityObject(entity) {
    const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const material = new THREE.MeshLambertMaterial({ color: entityColors[entityId] });
    const mesh = new THREE.Mesh(geometry, material);
    
    mesh.position.set(
        parseFloat(entity.position_x || 0),
        parseFloat(entity.position_y || 0),
        parseFloat(entity.position_z || 0)
    );
    
    scene.add(mesh);
    return mesh;
}
```

## Extending the Project

### Adding Custom 3D Models

Place your .obj, .fbx, or other 3D model files in the `client/models/` directory and reference them in the frontend code:

```javascript
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';

const loader = new OBJLoader();
loader.load('/models/your-model.obj', (object) => {
    scene.add(object);
});
```

### Adding New Entity Types

Extend the Rust module with new entity types:

```rust
#[spacetimedb::table]
#[derive(Clone, Debug, PartialEq, SpacetimeType)]
pub struct NewEntityType {
    #[spacetimedb::primarykey]
    pub id: u64,
    // Additional fields...
}
```

## Troubleshooting

- **Connection Issues**: Check that SpacetimeDB is running and accessible
- **Entity Creation Fails**: Verify that the Rust module is properly connected
- **3D Models Not Loading**: Ensure the models are in the correct format and location

## License

[MIT License](LICENSE)

## Acknowledgments

- [SpacetimeDB](https://spacetimedb.com/) - Multiplayer game database
- [Three.js](https://threejs.org/) - JavaScript 3D library
- [Quart](https://pgjones.gitlab.io/quart/) - Asynchronous Python web framework