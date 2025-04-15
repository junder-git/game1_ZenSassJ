import os
import json
import asyncio
import logging
from quart import Quart, websocket, render_template, send_from_directory, request
from spacetimedb_sdk.spacetimedb_client import SpacetimeDBClient
from spacetimedb_sdk.spacetimedb_client import Identity

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Define a simple autogen package - this is what's missing in your code
# This would typically be generated but we'll create a minimal one here
class AutogenPackage:
    @staticmethod
    def GameEntity(data):
        # Process the raw entity data
        return data

async def connect_to_spacetimedb():
    """Connect to SpacetimeDB using the SDK"""
    global client, connected_to_spacetime

    try:
        # Create a SpacetimeDB client instance with the required autogen_package
        client = SpacetimeDBClient(AutogenPackage)
        spacetime_url = f"ws://{SPACETIME_HOST}:{SPACETIME_PORT}"
        logger.info(f"Connecting to SpacetimeDB at {spacetime_url}")
        
        # Connect to the module
        logger.debug(f"Attempting to connect to module: {MODULE_NAME}")
        await client.connect(spacetime_url, MODULE_NAME)
        connected_to_spacetime = True
        logger.info("Connected to SpacetimeDB")
        
        # Subscribe to the GameEntity table
        logger.debug("Subscribing to GameEntity table")
        client.subscribe_table("GameEntity", on_entity_update)
        
        # Get all existing entities
        logger.debug("Querying existing entities")
        try:
            existing_entities = await client.query("get_all_entities", [])
            logger.info(f"Retrieved {len(existing_entities)} existing entities")
            for entity in existing_entities:
                entity_id = str(entity.get("id"))
                entities[entity_id] = entity
                
            logger.info(f"Loaded {len(entities)} existing entities")
        except Exception as e:
            logger.error(f"Error querying existing entities: {e}")
        
    except Exception as e:
        logger.error(f"Error connecting to SpacetimeDB: {e}")
        connected_to_spacetime = False
        client = None
        # Try to reconnect after a delay
        logger.info("Will attempt to reconnect in 5 seconds")
        await asyncio.sleep(5)
        asyncio.create_task(connect_to_spacetimedb())

def on_entity_update(entity, operation):
    """Callback for entity updates from SpacetimeDB"""
    entity_id = str(entity.get("id"))
    logger.debug(f"Entity update received: {entity_id}, operation: {operation}")
    
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
    logger.debug(f"Broadcasting to {len(active_connections)} clients")
    for ws in active_connections:
        try:
            await ws.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
            # The connection might be broken, we'll remove it later

@app.before_serving
async def startup():
    """Connect to SpacetimeDB when the application starts"""
    logger.info("Application starting up, connecting to SpacetimeDB")
    asyncio.create_task(connect_to_spacetimedb())

@app.websocket('/ws')
async def ws():
    """Handle WebSocket connections from clients"""
    logger.info("New WebSocket connection established")
    current_ws = websocket._get_current_object()
    active_connections.add(current_ws)
    try:
        # Send initial entity state
        logger.debug(f"Sending initial state with {len(entities)} entities")
        await current_ws.send(json.dumps({
            "type": "initial_state",
            "data": list(entities.values())
        }))
        
        # Handle messages from client
        while True:
            data = await current_ws.receive()
            message = json.loads(data)
            logger.debug(f"Received WebSocket message: {message['type']}")
            
            # Handle different message types
            if message["type"] == "create_entity":
                if client and connected_to_spacetime:
                    # Forward create entity request to SpacetimeDB
                    position = message.get("position", {})
                    logger.debug(f"Creating entity at position: {position}")
                    try:
                        entity_id = await client.call_reducer(
                            "create_entity", 
                            [
                                position.get("x", 0), 
                                position.get("y", 0), 
                                position.get("z", 0)
                            ]
                        )
                        logger.info(f"Created entity with ID: {entity_id}")
                    except Exception as e:
                        logger.error(f"Error creating entity: {e}")
                else:
                    logger.warning("Cannot create entity - not connected to SpacetimeDB")
            
            elif message["type"] == "update_entity":
                if client and connected_to_spacetime:
                    # Forward update entity request to SpacetimeDB
                    try:
                        entity_id = message.get("id")
                        position = message.get("position", {})
                        logger.debug(f"Updating entity {entity_id} position: {position}")
                        result = await client.call_reducer(
                            "update_entity_position",
                            [
                                entity_id,
                                position.get("x", 0),
                                position.get("y", 0),
                                position.get("z", 0)
                            ]
                        )
                        logger.info(f"Updated entity {entity_id}: {result}")
                    except Exception as e:
                        logger.error(f"Error updating entity: {e}")
                else:
                    logger.warning("Cannot update entity - not connected to SpacetimeDB")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(current_ws)

@app.route('/')
async def index():
    """Serve the main application page"""
    logger.debug("Serving index page")
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
    logger.info("Starting Quart application server")
    app.run(host='0.0.0.0', port=8080)