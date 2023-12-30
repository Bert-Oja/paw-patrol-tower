from typing import Any, Dict
import json
from openai_integration import ChatApp
from prompts import mission_prompt, translation_prompt_1, translation_prompt_2


def generate_new_mission_data() -> Dict[str, Any]:
    try:
        chat_app = ChatApp(
            mission_prompt,
            response_format={"type": "json_object"},
            temperature=1.4,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0.3,
        )

        mission_response = chat_app.chat("Generate one mission")
        mission_response_data: Dict[str, Any] = json.loads(mission_response)

        chat_app.messages = [{"role": "system", "content": translation_prompt_1}]
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
