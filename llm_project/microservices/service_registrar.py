from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

# Stores registered services
registered_services = {}

# Lock for thread safety
lock = threading.Lock()


@app.route("/register", methods=["POST"])
def register_service():
    """Registers a new service with the registrar."""
    data = request.json
    service_name = data.get("service_name")
    service_address = data.get("service_address")

    if not service_name or not service_address:
        return jsonify({"error": "Missing service_name or service_address"}), 400

    with lock:
        registered_services[service_name] = {
            "address": service_address,
            "last_seen": time.time()
        }

    return jsonify({"message": f"Service {service_name} registered successfully"}), 200


@app.route("/list", methods=["GET"])
def list_services():
    """Returns a list of active services."""
    with lock:
        active_services = {k: v["address"] for k, v in registered_services.items()}
    return jsonify(active_services)


@app.route("/forward", methods=["POST"])
def forward_message():
    """Forwards a message to another service."""
    data = request.json
    target_service = data.get("target_service")
    payload = data.get("payload")

    if not target_service or not payload:
        return jsonify({"error": "Missing target_service or payload"}), 400

    with lock:
        if target_service not in registered_services:
            return jsonify({"error": f"Service {target_service} not found"}), 404

        target_address = registered_services[target_service]["address"]

    # Forward the request
    try:
        response = requests.post(target_address, json=payload)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


def cleanup_services():
    """Removes services that haven't sent a heartbeat in 5 minutes."""
    while True:
        time.sleep(60)  # Run every 60 seconds
        with lock:
            now = time.time()
            to_remove = [k for k, v in registered_services.items() if now - v["last_seen"] > 300]

            for service in to_remove:
                del registered_services[service]
                print(f"Service {service} removed due to inactivity")


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    """Updates last_seen timestamp for a service."""
    data = request.json
    service_name = data.get("service_name")

    if service_name not in registered_services:
        return jsonify({"error": "Service not registered"}), 404

    with lock:
        registered_services[service_name]["last_seen"] = time.time()

    return jsonify({"message": f"Heartbeat received from {service_name}"}), 200


# Start cleanup thread
threading.Thread(target=cleanup_services, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5001)
