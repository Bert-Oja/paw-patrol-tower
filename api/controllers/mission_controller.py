from database import Session, Mission
from generators import generate_new_mission_data, create_audio_file


def add_mission(mission_data):
    session = Session()
    # Convert list of involved pups to a comma-separated string
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
    # Convert the mission to a dictionary
    mission_dict = {c.name: getattr(mission, c.name) for c in mission.__table__.columns}
    session.close()
    return mission_dict


def get_mission_by_id(mission_id):
    session = Session()
    mission = session.query(Mission).filter(Mission.id == mission_id).first()
    if mission:
        mission.is_requested = True
        session.commit()
    session.close()
    return mission


def get_mission_by_title(title):
    session = Session()
    mission = session.query(Mission).filter(Mission.mission_title == title).first()
    if mission:
        mission.is_requested = True
        session.commit()
    session.close()
    return mission


def get_latest_unrequested_mission():
    session = Session()
    mission = (
        session.query(Mission)
        .filter(Mission.is_requested == False)
        .order_by(Mission.id.desc())
        .first()
    )
    if mission:
        mission.is_requested = True
        session.commit()
    mission_dict = {c.name: getattr(mission, c.name) for c in mission.__table__.columns}
    session.close()
    return mission_dict


def maintain_mission_buffer(buffer_size=5):
    session = Session()
    unrequested_count = (
        session.query(Mission).filter(Mission.is_requested == False).count()
    )
    needed_missions = buffer_size - unrequested_count

    for _ in range(needed_missions):
        new_mission_data = generate_new_mission_data()
        new_mission = add_mission(new_mission_data)
        audio_file_name = f"mission_{new_mission.get('id')}"
        audio_script = new_mission.get("translation")
        # Create the audio file
        result = create_audio_file(audio_file_name, audio_script)

        # Check if the audio file was successfully created
        if result:
            print("Audio file created successfully.")
        else:
            print("Failed to create the audio file.")

    session.close()
