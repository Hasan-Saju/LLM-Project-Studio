from flask import Flask, request, jsonify
import requests
import threading
import time
import re

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

# Define common shorthand and their replacements
shorthand_corrections = {
    r"\bu\b": "you",
    r"\br\b": "are",
    r"\b4\b": "for",
    r"\bgr8\b": "great",
    r"\btho\b": "though",
    r"\bl8r\b": "later",
    r"\bpls\b": "please",
    r"\bthx\b": "thanks"
}

# Fact-checking dictionary for common misconceptions
fact_corrections = {
    r"\bearth is flat\b": "Earth is round",
    r"\bhumans use only 10% of their brain\b": "Humans use nearly all of their brain.",
    r"\bwater conducts electricity\b": "Pure water does not conduct electricity, but impurities do.",
    r"\bbananas grow on trees\b": "Bananas grow on plants, not trees."
}

# Function to apply corrections
def correct_text(text, corrections):
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
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

        # Apply shorthand correction
        fixed_message = correct_text(user_message, shorthand_corrections)

        # Apply fact-checking correction
        fixed_message = correct_text(fixed_message, fact_corrections)

        print("Fixed message:", fixed_message)
        return jsonify({"fixed_message": fixed_message})  # ✅ Always return clean JSON

    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(port=5002)
