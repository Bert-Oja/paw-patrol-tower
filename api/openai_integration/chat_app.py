from openai import OpenAI
import os

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL", "gpt-3.5-turbo-1106"
)  # Default to 'gpt-3.5-turbo-1106' if not set

##################################################################
### OPTIONS FOR CHAT COMPLETION ENDPOINT                       ###
###                                                            ###
### https://platform.openai.com/docs/api-reference/chat/create ###
##################################################################


class ChatApp:
    def __init__(self, system_message: str, **options):
        self.client = OpenAI()
        self.messages = [{"role": "system", "content": system_message}]
        self.options = options

    def chat(self, message):
        self.messages.append({"role": "user", "content": message})
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL, **self.options, messages=self.messages
            )
            assistant_message = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})
            return assistant_message
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
