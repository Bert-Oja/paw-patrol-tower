"""
This module provides the database functionality for the Paw Patrol Tower API.

The `Session` class represents a session in the database,
while the `Mission` class represents a mission.

Usage:
    from api.database import Session, Mission

    # Create a new session
    session = Session()

    # Create a new mission
    mission = Mission()

    # Perform database operations using the session and mission objects
"""
from .models import Session, Mission

__all__ = ["Session", "Mission"]
