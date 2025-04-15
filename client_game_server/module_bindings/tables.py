"""
Table definitions for spacetime-game-server SpacetimeDB module.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class GameEntity:
    """
    Represents a game entity in the SpacetimeDB.
    Maps to the GameEntity table in the Rust module.
    """
    id: int  # Primary key
    position_x: float
    position_y: float
    position_z: float
    owner: Any  # Identity type from SpacetimeDB
    created_at: Any  # Timestamp type from SpacetimeDB

    @classmethod
    def from_row(cls, row):
        """Convert a SpacetimeDB row to a GameEntity instance."""
        return cls(
            id=row.get('id'),
            position_x=row.get('position_x'),
            position_y=row.get('position_y'),
            position_z=row.get('position_z'),
            owner=row.get('owner'),
            created_at=row.get('created_at')
        )

    def to_dict(self):
        """Convert the GameEntity instance to a dictionary."""
        return {
            'id': self.id,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'position_z': self.position_z,
            'owner': self.owner,
            'created_at': self.created_at
        }