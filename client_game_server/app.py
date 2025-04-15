import os
import json
import asyncio
import aiohttp
from quart import Quart, websocket, render_template, send_from_directory, request

# Create Quart app
app = Quart(__name__)

# Configuration
SPACETIME_HOST = os.environ.get("SPACETIME_HOST", "localhost")
SPACETIME_PORT = os.environ.get("SPACETIME_PORT", "4000")
MODULE_NAME = "spacetime-game-server"

# Store for active websocket connections
active_connections = set()

# WebSocket connection to SpacetimeDB
spacetime_ws = None
connected_to_spacetime = False

# Entity data store
entities = {}


async def connect_to_spacetimedb():
    """Connect to SpacetimeDB and handle messages"""
    global spacetime_ws, connected_to_spacetime

    try:
        spacetime_url = f"ws://{SPACETIME_HOST}:{SPACETIME_PORT}/ws"
        print(f"Connecting to SpacetimeDB at {spacetime_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(spacetime_url) as ws:
                spacetime_ws = ws
                connected_to_spacetime = True
                print("Connected to SpacetimeDB")
                
                # Subscribe to the module
                subscribe_msg = {
                    "jsonrpc": "2.0",
                    "method": "subscribe",
                    "params": {"module_name": MODULE_NAME},
                    "id": 1
                }
                await ws.send_json(subscribe_msg)
                
                # Handle incoming messages
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await process_spacetime_message(data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print(f"SpacetimeDB connection error: {ws.exception()}")
                        break
    except Exception as e:
        print(f"Error connecting to SpacetimeDB: {e}")
    finally:
        connected_to_spacetime = False
        spacetime_ws = None
        # Try to reconnect after a delay
        await asyncio.sleep(5)
        asyncio.create_task(connect_to_spacetimedb())


async def process_spacetime_message(message):
    """Process messages from SpacetimeDB and broadcast updates to clients"""
    if "result" in message:
        result = message["result"]
        
        # Handle entity updates
        if "entities" in result:
            for entity_update in result["entities"]:
                entity_id = str(entity_update.get("id"))
                operation = entity_update.get("operation")
                
                if operation == "insert" or operation == "update":
                    entities[entity_id] = entity_update
                elif operation == "delete":
                    if entity_id in entities:
                        del entities[entity_id]
                
                # Broadcast to all clients
                await broadcast_to_clients({"type": "entity_update", "data": entity_update})


async def broadcast_to_clients(message):
    """Broadcast message to all connected clients"""
    for ws in active_connections:
        try:
            await ws.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending to client: {e}")
            # The connection might be broken, we'll remove it later


async def send_to_spacetimedb(method, params):
    """Send a message to SpacetimeDB"""
    if spacetime_ws and connected_to_spacetime:
        message = {
            "jsonrpc": "2.0", 
            "method": method,
            "params": params,
            "id": id(params)  # Use a unique ID
        }
        await spacetime_ws.send_json(message)
        return True
    return False


@app.before_serving
async def startup():
    """Connect to SpacetimeDB when the application starts"""
    asyncio.create_task(connect_to_spacetimedb())


@app.websocket('/ws')
async def ws():
    """Handle WebSocket connections from clients"""
    active_connections.add(websocket._get_current_object())
    try:
        # Send initial entity state
        await websocket.send(json.dumps({
            "type": "initial_state",
            "data": list(entities.values())
        }))
        
        # Handle messages from client
        while True:
            data = await websocket.receive()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "create_entity":
                # Forward create entity request to SpacetimeDB
                position = message.get("position", {})
                params = {
                    "reducer": "create_entity",
                    "args": [
                        position.get("x", 0), 
                        position.get("y", 0), 
                        position.get("z", 0)
                    ]
                }
                await send_to_spacetimedb("call_reducer", params)
            
            elif message["type"] == "update_entity":
                # Forward update entity request to SpacetimeDB
                entity_id = message.get("id")
                position = message.get("position", {})
                params = {
                    "reducer": "update_entity_position",
                    "args": [
                        entity_id,
                        position.get("x", 0),
                        position.get("y", 0),
                        position.get("z", 0)
                    ]
                }
                await send_to_spacetimedb("call_reducer", params)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket._get_current_object())


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