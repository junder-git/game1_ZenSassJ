"""
Reducer definitions for spacetime-game-server SpacetimeDB module.
"""

async def create_entity(client, position_x: float, position_y: float, position_z: float) -> int:
    """
    Call the create_entity reducer defined in the Rust module.
    
    Args:
        client: SpacetimeDBAsyncClient instance
        position_x: X coordinate of the entity's position
        position_y: Y coordinate of the entity's position
        position_z: Z coordinate of the entity's position
        
    Returns:
        Entity ID of the created entity
    """
    return await client.call_reducer("create_entity", [position_x, position_y, position_z])


async def update_entity_position(client, entity_id: int, position_x: float, position_y: float, position_z: float) -> bool:
    """
    Call the update_entity_position reducer defined in the Rust module.
    
    Args:
        client: SpacetimeDBAsyncClient instance
        entity_id: ID of the entity to update
        position_x: New X coordinate
        position_y: New Y coordinate
        position_z: New Z coordinate
        
    Returns:
        True if the update was successful, False otherwise
    """
    return await client.call_reducer("update_entity_position", [entity_id, position_x, position_y, position_z])