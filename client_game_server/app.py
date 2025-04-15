import os
import json
import asyncio
import sys
from quart import Quart, websocket, render_template, send_from_directory, request
from spacetimedb_sdk.spacetimedb_async_client import SpacetimeDBAsyncClient

# Import the module_bindings package
import module_bindings

# Create Quart app
app = Quart(__name__)

# Configuration
SPACETIME_HOST = os.environ.get("SPACETIME_HOST", "spacetimedb")
SPACETIME_PORT = os.environ.get("SPACETIME_PORT", "3000")
MODULE_NAME = os.environ.get("MODULE_NAME", "spacetime-game-server")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")  # Add this for authentication

# Store for active websocket connections
active_connections = set()

# SpacetimeDB client
client = None
connected_to_spacetime = False
connection_task = None

# Entity data store
entities = {}

async def on_connect():
    """Callback for when connection is established"""
    global connected_to_spacetime
    print(f"Connected to SpacetimeDB module: {MODULE_NAME}")
    connected_to_spacetime = True
    
    try:
        # Get all existing entities
        existing_entities = await module_bindings.get_all_entities(client)
        for entity in existing_entities:
            entity_id = str(entity.id)
            entities[entity_id] = entity.to_dict()
            
        print(f"Loaded {len(entities)} existing entities")
        
        # Notify all clients about the connection status
        await broadcast_to_clients({
            "type": "connection_status",
            "connected": True
        })
    except Exception as e:
        print(f"Error in on_connect: {e}")

def on_entity_update(entity, operation):
    """Callback for entity updates from SpacetimeDB"""
    # Convert to GameEntity instance if needed
    if not isinstance(entity, module_bindings.GameEntity):
        try:
            entity = module_bindings.GameEntity.from_row(entity)
        except Exception as e:
            print(f"Error converting entity: {e}")
            return
    
    entity_dict = entity.to_dict() if hasattr(entity, 'to_dict') else entity
    entity_id = str(entity_dict.get('id'))
    
    if operation == "insert" or operation == "update":
        entities[entity_id] = entity_dict
    elif operation == "delete":
        if entity_id in entities:
            del entities[entity_id]
    
    # Broadcast to all clients
    asyncio.create_task(broadcast_to_clients({
        "type": "entity_update", 
        "data": {
            **entity_dict,
            "operation": operation
        }
    }))

async def connect_to_spacetimedb():
    """Connect to SpacetimeDB using the run method"""
    global client, connected_to_spacetime
    
    retry_count = 0
    max_retries = 10
    retry_delay = 5  # seconds
    
    # Try to resolve the hostname first
    import socket
    print(f"Attempting to resolve hostname: {SPACETIME_HOST}")
    try:
        ip_address = socket.gethostbyname(SPACETIME_HOST)
        print(f"Resolved {SPACETIME_HOST} to IP: {ip_address}")
    except socket.gaierror as e:
        print(f"Warning: Could not resolve {SPACETIME_HOST}: {e}")
    
    try:
        print(f"Connecting to SpacetimeDB at {SPACETIME_HOST}:{SPACETIME_PORT}")
        
        # Create the SpacetimeDBAsyncClient instance with module bindings
        client = SpacetimeDBAsyncClient(autogen_package=module_bindings)
        
        # Set up connection URL
        spacetime_url = f"http://{SPACETIME_HOST}:{SPACETIME_PORT}"
        
        # Create a task for running the client
        # We need to create a task because run() is a blocking call that doesn't return
        connection_task = asyncio.create_task(
            client.run(
                AUTH_TOKEN,
                spacetime_url,
                MODULE_NAME,
                on_connect,
                ["SELECT * FROM GameEntity"]  # SQL-style subscription
            )
        )
        
        # The connection handling will happen in the on_connect callback
        # which will be called when the connection is established
        
        # Return the task so it doesn't get garbage collected
        return connection_task
            
    except Exception as e:
        print(f"Error connecting to SpacetimeDB: {e}")
        print(f"Error details: {type(e).__name__}, {str(e)}")
        connected_to_spacetime = False
        client = None
        
        # Retry after delay
        await asyncio.sleep(retry_delay)
        return await connect_to_spacetimedb()

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
    # Create the connection task and store it
    global connection_task
    connection_task = await connect_to_spacetimedb()

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
        
        # Send connection status
        await current_ws.send(json.dumps({
            "type": "connection_status",
            "connected": connected_to_spacetime
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
                        entity_id = await module_bindings.create_entity(
                            client,
                            position.get("x", 0), 
                            position.get("y", 0), 
                            position.get("z", 0)
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
                        result = await module_bindings.update_entity_position(
                            client,
                            entity_id,
                            position.get("x", 0),
                            position.get("y", 0),
                            position.get("z", 0)
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