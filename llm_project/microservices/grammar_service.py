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
        try:
            requests.post("http://localhost:5001/heartbeat", json={"service_name": SERVICE_NAME})
            print(f"Sent heartbeat for {SERVICE_NAME}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send heartbeat: {e}")

# Register this service with the service registrar
try:
    response = requests.post(REGISTRAR_URL, json={"service_name": SERVICE_NAME, "service_address": SERVICE_ADDRESS})
    print("Service registered:", response.status_code, response.text)
except requests.exceptions.RequestException as e:
    print(f"Service registration failed: {e}")

# Start heartbeat thread
threading.Thread(target=send_heartbeat, daemon=True).start()

@app.route("/process", methods=["POST"])
def process_prompt():
    """Fixes grammar and fact-checks the user prompt."""
    try:
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "Invalid or missing message"}), 400

        user_message = data["message"]
        print("Received message:", user_message)

        # Simple grammar fix (Replace with AI model if needed)
        fixed_message = user_message.replace("u", "you").replace("r", "are")

        # Fact-checking logic (simplified)
        if "earth is flat" in fixed_message.lower():
            fixed_message = fixed_message.replace("earth is flat", "Earth is round")

        print("Fixed message:", fixed_message)
        return jsonify({"fixed_message": fixed_message})  # ✅ Always return clean JSON

    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(port=5002)
