from openai_integration import ChatApp
from prompts import mission_prompt
from database import Session, Mission
from generators import generate_new_mission_data, create_audio_file
import logging


def add_mission(mission_data, session):
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
    except Exception as e:
        logging.error(f"Error adding mission to the database: {e}")
        print(f"Error adding mission to the database: {e}")
        return None


def get_mission_by_id(mission_id):
    session = Session()
    mission = session.query(Mission).filter(Mission.id == mission_id).first()
    if mission:
        mission.is_requested = True
        session.commit()
    session.close()
    return mission.to_dict() if mission else None


def get_mission_by_title(title):
    session = Session()
    mission = session.query(Mission).filter(Mission.mission_title == title).first()
    if mission:
        mission.is_requested = True
        session.commit()
    session.close()
    return mission.to_dict() if mission else None


def get_latest_unrequested_mission():
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
    session.close()
    return mission.to_dict() if mission else None


def delete_mission(mission_id, session):
    try:
        mission = session.query(Mission).get(mission_id)
        if mission:
            session.delete(mission)
            session.commit()
    except Exception as e:
        logging.error(f"Error deleting mission from the database: {e}")
        print(f"Error deleting mission from the database: {e}")


def maintain_mission_buffer(buffer_size=5):
    session = Session()
    try:
        chat_app = ChatApp(
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=4095,
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
