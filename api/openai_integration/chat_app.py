from openai import OpenAI
import os
import logging

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL", "gpt-3.5-turbo-1106"
)  # Default to 'gpt-3.5-turbo-1106' if not set

##################################################################
### OPTIONS FOR CHAT COMPLETION ENDPOINT                       ###
###                                                            ###
### https://platform.openai.com/docs/api-reference/chat/create ###
##################################################################


class ChatApp:
    def __init__(self, **options):
        self.client = OpenAI()
        self.options = options
        logging.info(f"Chat app options: {self.options}")

    def set_system_message(self, system_message: str):
        self.messages = [{"role": "system", "content": system_message}]
        
    def chat(self, message):
        self.messages.append({"role": "user", "content": message})
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL, **self.options, messages=self.messages
            )
            assistant_message = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})
            # Create an object including the full chat history and relevant metadata like the id of the session
            logging.info(f"Chat app response: {response}")
            return assistant_message
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            return None
