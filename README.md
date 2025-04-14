# SpacetimeDB Three.js Game Setup

This project contains a full SpacetimeDB setup with three containers:
1. SpacetimeDB - The database and server platform
2. Rust Server Module - The game logic written in Rust
3. TypeScript/Three.js Client - The 3D frontend client

## Project Structure

```
.
├── docker-compose.yml       # Main Docker Compose configuration
├── server/                  # Rust server module
│   ├── Dockerfile          # Server container configuration 
│   ├── Cargo.toml          # Rust dependencies and project configuration
│   └── src/
│       └── lib.rs          # Server game logic
├── client/                  # TypeScript/Three.js client
│   ├── Dockerfile          # Client container configuration
│   ├── package.json        # Node.js dependencies
│   ├── tsconfig.json       # TypeScript configuration
│   ├── webpack.config.js   # Webpack configuration
│   └── src/
│       ├── index.html      # Client HTML template
│       └── index.ts        # Client game logic
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

3. Access the client in your browser at: http://localhost:8080
4. Access the SpacetimeDB web interface at: http://localhost:3000

## Development Workflow

### Server Development (Rust)

1. Modify the Rust code in the `server/src` directory
2. The container will automatically rebuild and reload when changes are detected

### Client Development (TypeScript/Three.js)

1. Modify the TypeScript code in the `client/src` directory  
2. The client container uses webpack dev server with hot reloading
3. Changes will be reflected in the browser automatically

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