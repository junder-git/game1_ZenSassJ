# SpacetimeDB Game Setup with Python Quart

(((Mimic the ts types with raw es6 js classes and inject them into the db instead)))

This project contains a full SpacetimeDB setup with three containers:
1. SpacetimeDB - The database and server platform
2. Rust Server Module - The game logic written in Rust
3. Python Quart Application - The web client and server intermediary

## Project Structure

```
.
├── docker-compose.yml       # Main Docker Compose configuration
├── server/                  # Rust server module
│   ├── Dockerfile          # Server container configuration 
│   ├── Cargo.toml          # Rust dependencies and project configuration
│   └── src/
│       └── lib.rs          # Server game logic
├── client/                  # Python Quart application
│   ├── Dockerfile          # Client container configuration
│   ├── app.py              # Main Quart application
│   ├── requirements.txt    # Python dependencies
│   ├── templates/          # HTML templates
│   │   └── index.html      # Main page template
│   ├── static/             # Static files
│   │   └── main.css        # CSS styles
│   └── models/             # 3D model files (optional)
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone this repository)

### Running the Project

1. Create the project structure and files as shown above
2. Start all containers using Docker Compose:

```bash
docker-compose up --build
```

3. Access the application in your browser at: http://localhost:8080
4. Access the SpacetimeDB web interface at: http://localhost:3000

### Working with 3D Models

The Quart application is configured to serve 3D model files from the `client/models/` directory. You can place your .obj, .fbx, and other 3D model files there and reference them in your HTML/JavaScript code.

To load a model:

```javascript
// Example using Three.js to load an OBJ model
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';

const loader = new OBJLoader();
loader.load('/models/your-model.obj', (object) => {
    scene.add(object);
});
```

## Development Workflow

### Server Development (Rust)

1. Modify the Rust code in the `server/src` directory
2. The container will automatically rebuild and reload when changes are detected

### Client Development (Python Quart)

1. Modify the Python code in the `client` directory
2. The container mounts the client directory as a volume, so changes are reflected immediately
3. Quart includes auto-reloading by default, so most changes will be applied without restarting

## Game Controls

- Press "C" or click the "Create Entity" button to create a new random entity
- Use mouse to orbit the camera around the scene

## Game Controls

- Press "c" to create a new random entity
- Use mouse to orbit the camera around the scene

## Customizing the Project

### Adding New Game Entities

1. Define new entities in the `server/src/lib.rs` file
2. Add corresponding TypeScript interfaces in the client code
3. Subscribe to the new entities in the client code

### Extending the 3D Visualization

1. Modify the Three.js scene setup in `client/src/index.ts`
2. Add new 3D models, textures, or effects as needed

## Deploying to Production

For production deployment:

1. Update the `docker-compose.yml` file to use specific version tags instead of `latest`
2. Configure proper volume mounts for persistent data
3. Set up proper network security and access controls

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

- If the client can't connect to SpacetimeDB, check the environment variables in the docker-compose.yml
- For Rust compilation errors, check the server container logs
- For client issues, inspect the browser console for JavaScript errors
