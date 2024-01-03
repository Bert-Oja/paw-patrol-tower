"""
This module provides the model functionality for the Paw Patrol Tower API.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

directory_path = os.getenv("DATABASE_DIRECTORY_PATH", "/data/database")
os.makedirs(directory_path, exist_ok=True)

database_name = os.getenv("DATABASE_NAME", "mission_database.db")

# Create an engine that stores data in the specified path
engine = create_engine(f"sqlite:///{directory_path}/{database_name}")

Base = declarative_base()


class Mission(Base):
    """
    Represents a mission in the Paw Patrol Tower database.

    Attributes:
        id (int): The unique identifier of the mission.
        mission_title (str): The title of the mission.
        involved_pups (str): The pups involved in the mission, stored as a comma-separated string.
        main_location (str): The main location of the mission.
        mission_script (str): The script of the mission.
        translation (str): The translation of the mission.
        is_requested (bool): Indicates if the mission is requested or not.

    Methods:
        __repr__(): Returns a string representation of the Mission object.
        to_dict(): Returns a dictionary representation of the Mission object.
    """

    __tablename__ = "missions"

    id = Column(Integer, primary_key=True)
    mission_title = Column(String)
    involved_pups = Column(String)
    main_location = Column(String)
    mission_script = Column(Text)
    translation = Column(Text)
    is_requested = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f"<Mission(title='{self.mission_title}', location='{self.main_location}')>"
        )

    def to_dict(self):
        """
        Convert the object to a dictionary representation.

        Returns:
            dict: A dictionary containing the object's attributes.
        """
        return {
            "id": self.id,
            "mission_title": self.mission_title,
            "involved_pups": self.involved_pups,
            "main_location": self.main_location,
            "mission_script": self.mission_script,
            "translation": self.translation,
            "is_requested": self.is_requested,
        }


# Create all tables in the engine
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session: sessionmaker = sessionmaker(bind=engine)
