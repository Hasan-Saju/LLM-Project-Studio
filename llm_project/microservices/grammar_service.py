from flask import Flask, request, jsonify
# from config import SERVICE_NAME, SERVICE_ADDRESS, REGISTRAR_URL, HEART_BEAT_URL
from dotenv import load_dotenv
import requests
import threading
import time
import re
import os

load_dotenv()
SERVICE_NAME = os.getenv("SERVICE_NAME")
SERVICE_ADDRESS = os.getenv("SERVICE_ADDRESS")
REGISTRAR_URL = os.getenv("REGISTRAR_URL")
HEART_BEAT_URL = os.getenv("HEART_BEAT_URL")

app = Flask(__name__)

def send_heartbeat():
    while True:
        time.sleep(120)
        try:
            requests.post(HEART_BEAT_URL, json={"service_name": SERVICE_NAME})
            print(f"Sent heartbeat for {SERVICE_NAME}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send heartbeat: {e}")

# Register this service with the service registrar
try:
    response = requests.post(REGISTRAR_URL, json={"service_name": SERVICE_NAME, "service_address": SERVICE_ADDRESS})
    print("Service registered:", response.status_code, response.text)
except requests.exceptions.RequestException as e:
    print(f"Service registration failed: {e}")


shorthand_corrections = {
    r"\bu\b": "you",
    r"\br\b": "are",
    r"\b4\b": "for",
    r"\bgr8\b": "great",
    r"\btho\b": "though",
    r"\bl8r\b": "later",
    r"\bpls\b": "please",
    r"\bthx\b": "thanks",
    r"\bdefinately\b": "definitely",
    r"\brecieve\b": "receive",
    r"\bseperate\b": "separate",
    r"\bteh\b": "the",
    r"\boccured\b": "occurred",
    r"\bwich\b": "which",
    r"\bdplrning\b": "deeplearning",
    r"\bxplain\b": "explain",
    r"\bw8\b": "what",
    r"\bes\b": "is",
    r"\bcapitol\b": "capital",
    r"\bbd\b": "Bangladesh",
}



fact_corrections = {
    r"\bearth is flat\b": "Earth is round",
    r"\bhumans use only 10% of their brain\b": "Humans use nearly all of their brain.",
    r"\bwater conducts electricity\b": "Pure water does not conduct electricity, but impurities do.",
    r"\bbananas grow on trees\b": "Bananas grow on plants, not trees.",
    r"\bmount everest is the tallest mountain\b": "Mauna Kea is the tallest mountain when measured from base to peak.",
    r"\bthe great wall of china is visible from space\b": "The Great Wall of China is not visible from space with the naked eye.",
    r"\bwe have five senses\b": "Humans have more than five senses, including balance and temperature perception.",
    r"\bgoldfish have a three-second memory\b": "Goldfish have a memory span of months, not seconds.",
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
        return jsonify({"fixed_message": fixed_message})

    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002) 

