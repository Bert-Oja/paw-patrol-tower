"""
This module contains the main Flask application for the Paw Patrol Tower API.

The API provides endpoints for retrieving missions and mission audio files.

Endpoints:
- /mission: GET request to retrieve the latest unrequested mission.
- /mission-audio/<int:id>: GET request to retrieve the audio file for a specific mission.

The module also includes a background thread for maintaining the mission buffer.

Classes:
- PrettyLogger: Custom logger class that formats log messages in a pretty way.

Functions:
- run_mission_buffer_maintenance: Function that runs the mission buffer maintenance thread.

"""

import os
import sys
from threading import Thread
import time
import logging
import pprint

# Pylint Disable for specific import order
# pylint: disable=wrong-import-order,wrong-import-position
from dotenv import load_dotenv

load_dotenv()
# pylint: enable=wrong-import-order,wrong-import-position

from flask import Flask, jsonify, send_file
from api.controllers import maintain_mission_buffer, get_latest_unrequested_mission


# Check that the OPENAI_API_KEY environment variable is set and exit if not
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY environment variable not set")
    sys.exit(1)

# Fetch the log directory path from environment variable or set default
log_directory = os.getenv("LOG_DIRECTORY_PATH", "/data/logs")

# Ensure the directory exists
os.makedirs(log_directory, exist_ok=True)

# Log file path
log_file_path = os.path.join(log_directory, "mission_control.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=log_file_path,  # Logs are written to this file
    filemode="a",  # 'a' for append, 'w' for overwrite
)


class PrettyLogger(logging.Logger):
    """
    Custom logger class that formats log messages in a pretty way.
    """

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        if args:
            msg = msg % tuple(pprint.pformat(a) for a in args)
        super()._log(level, msg, (), exc_info, extra, stack_info)


logging.setLoggerClass(PrettyLogger)


def run_mission_buffer_maintenance():
    """
    Function that runs the mission buffer maintenance thread.

    The function is executed in a background thread and periodically maintains the mission buffer.
    """
    logging.info("Starting mission buffer maintenance thread")
    while True:
        mission_buffer = int(os.getenv("MISSION_BUFFER_SIZE", "5"))
        maintain_mission_buffer(mission_buffer)
        time.sleep(
            60 * 15
        )  # Run every 15 minutes as the max run time including retries is 12 minutes for 5 missions


# Start the background thread
buffer_thread = Thread(target=run_mission_buffer_maintenance)
buffer_thread.daemon = (
    True  # This ensures that the thread will close when the main process exits
)
buffer_thread.start()

app = Flask(__name__)


@app.route("/mission", methods=["GET"])
def get_mission():
    """
    Endpoint for retrieving the latest unrequested mission.

    Returns:
    - JSON response containing the latest unrequested mission.
    """
    return jsonify(get_latest_unrequested_mission())


@app.route("/mission-audio/<int:mission_id>", methods=["GET"])
def get_mission_audio(mission_id):
    """
    Endpoint for retrieving the audio file for a specific mission.

    Args:
    - id: The ID of the mission.

    Returns:
    - The audio file for the specified mission if it exists, or a 404 error if not found.
    """
    audio_file = f"mission_{mission_id}.wav"
    audio_path = os.path.join(
        os.getenv("AUDIO_DIRECTORY_PATH", "data/audio"), audio_file
    )

    if os.path.exists(audio_path):
        return send_file(audio_path)
    else:
        return "Audio file not found", 404


if __name__ == "__main__":
    # Start the Flask app
    app.run(debug=True, use_reloader=False)
