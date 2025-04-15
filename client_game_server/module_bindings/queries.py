"""
Query definitions for spacetime-game-server SpacetimeDB module.
"""
from typing import List
from .tables import GameEntity


async def get_all_entities(client) -> List[GameEntity]:
    """
    Call the get_all_entities query defined in the Rust module.
    
    Args:
        client: SpacetimeDBAsyncClient instance
        
    Returns:
        List of GameEntity objects
    """
    result = await client.query("get_all_entities", [])
    return [GameEntity.from_row(row) for row in result]