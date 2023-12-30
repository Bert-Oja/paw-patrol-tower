from flask import Flask, jsonify, send_file
import os
from dotenv import load_dotenv
from threading import Thread
import time

load_dotenv()
from controllers import maintain_mission_buffer, get_latest_unrequested_mission


def run_mission_buffer_maintenance():
    while True:
        maintain_mission_buffer()
        time.sleep(60 * 5)  # Run every 10 minutes, adjust the timing as needed


# Start the background thread
buffer_thread = Thread(target=run_mission_buffer_maintenance)
buffer_thread.daemon = (
    True  # This ensures that the thread will close when the main process exits
)
buffer_thread.start()


app = Flask(__name__)


@app.route("/mission", methods=["GET"])
def get_mission():
    return jsonify(get_latest_unrequested_mission())


@app.route("/mission-audio/<int:id>", methods=["GET"])
def get_mission_audio(id):
    audio_file = f"mission_{id}.wav"
    audio_path = os.path.join("data/audio", audio_file)

    if os.path.exists(audio_path):
        return send_file(audio_path)
    else:
        return "Audio file not found", 404


if __name__ == "__main__":
    app.run(debug=True)
