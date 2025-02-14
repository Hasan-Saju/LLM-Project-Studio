from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

SERVICE_NAME = "grammar_service"
SERVICE_ADDRESS = "http://localhost:5002/process"
REGISTRAR_URL = "http://localhost:5001/register"

# Function to send heartbeat every 2 minutes
def send_heartbeat():
    while True:
        time.sleep(120)
        requests.post("http://localhost:5001/heartbeat", json={"service_name": SERVICE_NAME})

# Register this service with the service registrar
requests.post(REGISTRAR_URL, json={"service_name": SERVICE_NAME, "service_address": SERVICE_ADDRESS})

# Start heartbeat thread
threading.Thread(target=send_heartbeat, daemon=True).start()

@app.route("/process", methods=["POST"])
def process_prompt():
    """Fixes grammar and fact-checks the user prompt."""
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Simple grammar fix (Replace this with an AI model if needed)
    fixed_message = user_message.replace("u", "you").replace("r", "are")

    # Fact-checking logic (simplified)
    if "earth is flat" in fixed_message.lower():
        fixed_message = fixed_message.replace("earth is flat", "Earth is round")

    return jsonify({"fixed_message": fixed_message})

if __name__ == "__main__":
    app.run(port=5002)
