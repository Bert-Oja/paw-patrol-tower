# main.py
# Prototype retrieving openai output
# - Get Paw Patrol mission details
# - Create initial translation
# - Refine translation
# - Create audio file via TTS endpoint
from openai import OpenAI
from openai.types import Completion
import json
from dotenv import load_dotenv
from prompts import mission_prompt, translation_prompt_1, translation_prompt_2

load_dotenv()

OPENAI_MODEL = "gpt-3.5-turbo-1106"


class ChatApp:
    def __init__(self, system_message: str, **options):
        # Setting the API key to use the OpenAI API
        self.client = OpenAI()
        self.messages = [
            {"role": "system", "content": system_message},
        ]
        self.options = options

    def chat(self, message):
        self.messages.append({"role": "user", "content": message})
        response: Completion = self.client.chat.completions.create(
            model=OPENAI_MODEL, **self.options, messages=self.messages
        )
        self.messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )
        return response.choices[0].message.content


mission_chat = ChatApp(
    mission_prompt,
    response_format={"type": "json_object"},
    temperature=1.4,
    max_tokens=4095,
    top_p=1,
    frequency_penalty=0.3,
)

mission_response = mission_chat.chat("Generate one mission")
# mission_response_object = json.loads(mission_response)
mission_response_data = json.loads(mission_response)

translation_chat = ChatApp(translation_prompt_1, temperature=1.2)
translation_response_1 = translation_chat.chat(
    mission_response_data.get("mission_script")
)
translation_response_2 = translation_chat.chat(translation_prompt_2)

mission_response_data["translation"] = translation_response_2

print(json.dumps(mission_response_data))
