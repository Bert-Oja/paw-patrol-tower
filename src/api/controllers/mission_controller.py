"""
This module contains functions for managing missions in the Paw Patrol Tower API.
"""
import logging
import os
from typing import Dict
from sqlalchemy.exc import SQLAlchemyError
from api.openai_integration import ChatApp
from api.database import Session, Mission
from api.generators import generate_new_mission_data, create_audio_file

# pylint: disable=singleton-comparison


def add_mission(mission_data: Dict[str, any], session: Session):
    """
    Add a new mission to the database.

    Args:
        mission_data (dict): The data of the mission to be added.
        session (Session): The database session.

    Returns:
        dict: The added mission data if successful, None otherwise.
    """
    try:
        involved_pups_str = ",".join(mission_data.get("involved_pups", []))
        mission = Mission(
            mission_title=mission_data["mission_title"],
            involved_pups=involved_pups_str,
            main_location=mission_data["main_location"],
            mission_script=mission_data["mission_script"],
            translation=mission_data["translation"],
        )
        session.add(mission)
        session.commit()
        return mission.to_dict()

    except KeyError as e:  # Specific exception for missing dictionary keys
        logging.error("KeyError: Missing data in mission_data: %s", e)
        print(f"KeyError: Missing data in mission_data: {e}")

    except SQLAlchemyError as e:  # Base class for all SQLAlchemy exceptions
        logging.error("Database error: %s", e)
        print(f"Database error: {e}")

    logging.error("Failed to add mission to the database.")
    return None  # Return None outside of the try-except block


def get_mission_by_id(mission_id):
    """
    Get a mission by its ID.

    Args:
        mission_id (int): The ID of the mission.

    Returns:
        dict: The mission data if found, None otherwise.
    """
    return_data = None
    session = Session()
    mission = session.query(Mission).filter(Mission.id == mission_id).first()
    if mission:
        mission.is_requested = True
        session.commit()
        return_data = mission.to_dict()
    session.close()
    return return_data


def get_mission_by_title(title):
    """
    Get a mission by its title.

    Args:
        title (str): The title of the mission.

    Returns:
        dict: The mission data if found, None otherwise.
    """
    return_data = None
    session = Session()
    mission = session.query(Mission).filter(Mission.mission_title == title).first()
    if mission:
        mission.is_requested = True
        session.commit()
        return_data = mission.to_dict()
    session.close()
    return return_data


def get_latest_unrequested_mission():
    """
    Get the latest unrequested mission.

    Returns:
        dict: The mission data if found, None otherwise.
    """
    return_data = None
    session = Session()
    mission = (
        session.query(Mission)
        .filter(Mission.is_requested == False)
        .order_by(Mission.id.asc())
        .first()
    )
    if mission:
        mission.is_requested = True
        session.commit()
        return_data = mission.to_dict()
    session.close()
    return return_data


def delete_mission(mission_id, session):
    """
    Delete a mission from the database.

    Args:
        mission_id (int): The ID of the mission.
        session: The database session.
    """
    try:
        mission = session.query(Mission).get(mission_id)
        if mission:
            session.delete(mission)
            session.commit()
    except SQLAlchemyError as e:
        logging.error("Error deleting mission from the database: %s", e)
        print("Error deleting mission from the database: %s", e)


def maintain_mission_buffer(buffer_size=5):
    """
    Maintain the mission buffer by generating new missions.

    Args:
        buffer_size (int): The desired size of the mission buffer.
    """
    session = Session()
    try:
        chat_app = ChatApp(
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2048")),
            top_p=1,
            frequency_penalty=0.3,
        )
        while True:
            unrequested_count = (
                session.query(Mission).filter(Mission.is_requested == False).count()
            )
            if unrequested_count >= buffer_size:
                break

            # Fetch the latest mission
            latest_mission = session.query(Mission).order_by(Mission.id.desc()).first()
            latest_mission_data = None
            if latest_mission:
                latest_mission_data = latest_mission.to_dict()

            new_mission_data = generate_new_mission_data(latest_mission_data, chat_app)
            if new_mission_data is None:
                continue

            new_mission = add_mission(new_mission_data, session)
            if new_mission is None:
                continue

            audio_file_name = f"mission_{new_mission.get('id')}"
            audio_script = new_mission.get("translation")
            if not create_audio_file(audio_file_name, audio_script):
                logging.error(
                    "Failed to create the audio file after retries. Deleting the mission entry."
                )
                print(
                    "Failed to create the audio file after retries. Deleting the mission entry."
                )
                delete_mission(new_mission.get("id"), session)
            else:
                logging.info("Audio file created successfully.")
                print("Audio file created successfully.")
    finally:
        session.close()


# pylint: enable=singleton-comparison
