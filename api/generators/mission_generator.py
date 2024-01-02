from typing import Any, Dict
import json
from openai_integration import ChatApp
from prompts import mission_prompt, translation_prompt_1, translation_prompt_2
import logging


def generate_new_mission_data(previous_mission: Dict = None, chat_app: ChatApp = None) -> Dict[str, Any]:
    try:
        # Create a new chat app if none is provided
        if chat_app == None:
            chat_app = ChatApp(
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=4095,
                top_p=1,
                frequency_penalty=0.3,
            )
        
        # Generate a new mission
        chat_app.set_system_message(mission_prompt)
        # If no previous mission is provided, just generate a new mission
        if previous_mission == None:
            user_message = "Generate one mission"
        else:
            user_message = f"Generate one mission. Make sure that the location is not set to {previous_mission.get('main_location')}, the involved pups are not included in this list: {previous_mission.get('involved_pups')} and the title is not similar to \"{previous_mission.get('mission_title')}\""
        
        mission_response = chat_app.chat(user_message)
        
        mission_response_data: Dict[str, Any] = json.loads(mission_response)

        # Translate the mission script
        chat_app.set_system_message(translation_prompt_1)
        
        translation_response_1 = chat_app.chat(
            mission_response_data.get("mission_script")
        )
        
        chat_app.messages = [{"role": "system", "content": translation_prompt_2}]
        translation_response_2: Dict[str, Any] = json.loads(
            chat_app.chat(translation_response_1)
        )
        
        mission_response_data["translation"] = translation_response_2.get("translation")

        return mission_response_data
    except json.JSONDecodeError:
        print("Failed to parse JSON response")
        logging.error("Failed to parse JSON response")
        return None
