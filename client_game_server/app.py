import os
import json
import asyncio
from quart import Quart, websocket, render_template, send_from_directory, request
from spacetimedb_sdk.spacetimedb_client import SpacetimeDBClient
# In 0.5.0, Identity might be in a different module or not required
# Let's remove the import for now and use string identifiers instead

# Create Quart app
app = Quart(__name__)

# Configuration
SPACETIME_HOST = os.environ.get("SPACETIME_HOST", "localhost")
SPACETIME_PORT = os.environ.get("SPACETIME_PORT", "4000")
MODULE_NAME = "spacetime-game-server"

# Store for active websocket connections
active_connections = set()

# SpacetimeDB client
client = None
connected_to_spacetime = False

# Entity data store
entities = {}

async def connect_to_spacetimedb():
    """Connect to SpacetimeDB using the SDK"""
    global client, connected_to_spacetime

    try:
        # Create a SpacetimeDB client instance
        client = SpacetimeDBClient()
        spacetime_url = f"ws://{SPACETIME_HOST}:{SPACETIME_PORT}"
        print(f"Connecting to SpacetimeDB at {spacetime_url}")
        
        # Connect to the module
        await client.connect(spacetime_url, MODULE_NAME)
        connected_to_spacetime = True
        print("Connected to SpacetimeDB")
        
        # Subscribe to the GameEntity table
        client.subscribe_table("GameEntity", on_entity_update)
        
        # Get all existing entities
        existing_entities = await client.query("get_all_entities", [])
        for entity in existing_entities:
            entity_id = str(entity.get("id"))
            entities[entity_id] = entity
            
        print(f"Loaded {len(entities)} existing entities")
        
    except Exception as e:
        print(f"Error connecting to SpacetimeDB: {e}")
        connected_to_spacetime = False
        client = None
        # Try to reconnect after a delay
        await asyncio.sleep(5)
        asyncio.create_task(connect_to_spacetimedb())

def on_entity_update(entity, operation):
    """Callback for entity updates from SpacetimeDB"""
    entity_id = str(entity.get("id"))
    
    if operation == "insert" or operation == "update":
        entities[entity_id] = entity
    elif operation == "delete":
        if entity_id in entities:
            del entities[entity_id]
    
    # Broadcast to all clients
    asyncio.create_task(broadcast_to_clients({
        "type": "entity_update", 
        "data": {
            **entity,
            "operation": operation
        }
    }))

async def broadcast_to_clients(message):
    """Broadcast message to all connected clients"""
    for ws in active_connections:
        try:
            await ws.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending to client: {e}")
            # The connection might be broken, we'll remove it later

@app.before_serving
async def startup():
    """Connect to SpacetimeDB when the application starts"""
    asyncio.create_task(connect_to_spacetimedb())

@app.websocket('/ws')
async def ws():
    """Handle WebSocket connections from clients"""
    current_ws = websocket._get_current_object()
    active_connections.add(current_ws)
    try:
        # Send initial entity state
        await current_ws.send(json.dumps({
            "type": "initial_state",
            "data": list(entities.values())
        }))
        
        # Handle messages from client
        while True:
            data = await current_ws.receive()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "create_entity":
                if client and connected_to_spacetime:
                    # Forward create entity request to SpacetimeDB
                    position = message.get("position", {})
                    try:
                        entity_id = await client.call_reducer(
                            "create_entity", 
                            [
                                position.get("x", 0), 
                                position.get("y", 0), 
                                position.get("z", 0)
                            ]
                        )
                        print(f"Created entity with ID: {entity_id}")
                    except Exception as e:
                        print(f"Error creating entity: {e}")
            
            elif message["type"] == "update_entity":
                if client and connected_to_spacetime:
                    # Forward update entity request to SpacetimeDB
                    try:
                        entity_id = message.get("id")
                        position = message.get("position", {})
                        result = await client.call_reducer(
                            "update_entity_position",
                            [
                                entity_id,
                                position.get("x", 0),
                                position.get("y", 0),
                                position.get("z", 0)
                            ]
                        )
                        print(f"Updated entity {entity_id}: {result}")
                    except Exception as e:
                        print(f"Error updating entity: {e}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        active_connections.remove(current_ws)

@app.route('/')
async def index():
    """Serve the main application page"""
    return await render_template('index.html')

@app.route('/static/<path:path>')
async def static_files(path):
    """Serve static files"""
    return await send_from_directory('static', path)

@app.route('/models/<path:path>')
async def serve_models(path):
    """Serve 3D model files"""
    return await send_from_directory('models', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)