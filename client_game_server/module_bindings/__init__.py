"""
Module bindings for spacetime-game-server SpacetimeDB module.
"""

from .tables import GameEntity
from .reducers import create_entity, update_entity_position
from .queries import get_all_entities

__all__ = [
    'GameEntity',
    'create_entity',
    'update_entity_position',
    'get_all_entities',
]