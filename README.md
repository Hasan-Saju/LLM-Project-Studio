# LLM Project Studio

Welcome to the LLM Project Studio! This is a Django-based project that integrates with Ollama. The project is containerized using Docker for easy deployment.

## 📌 Table of Contents

- [LLM Project Studio](#llm-project-studio)
  - [📌 Table of Contents](#-table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Assignment 1: Running the Project Locally](#assignment-1-running-the-project-locally)
      - [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
      - [2️⃣ Create a Virtual Environment](#2️⃣-create-a-virtual-environment)
      - [3️⃣ Install Dependencies](#3️⃣-install-dependencies)
      - [4️⃣ Run Migrations](#4️⃣-run-migrations)
      - [5️⃣ Start the Django Server](#5️⃣-start-the-django-server)
  - [Running the Project with Docker](#running-the-project-with-docker)
      - [1️⃣ Build the Docker Image](#1️⃣-build-the-docker-image)
      - [2️⃣ Run the Container](#2️⃣-run-the-container)
  - [Environment Variables](#environment-variables)
  - [Preview](#preview)
- [Assignment 2: Service Discovery](#assignment-2-service-discovery)
  - [Service Registry - Microservices Discovery and Communication](#service-registry---microservices-discovery-and-communication)
  - [Overview](#overview)
  - [Features](#features)
  - [Technologies Used](#technologies-used)
  - [Running the Service Registry](#running-the-service-registry)
  - [API Endpoints](#api-endpoints)
    - [1. Register a Service](#1-register-a-service)
    - [2. List All Services](#2-list-all-services)
    - [3. Send Heartbeat](#3-send-heartbeat)
    - [4. Forward a Message to Another Service](#4-forward-a-message-to-another-service)
  - [Service Cleanup Process](#service-cleanup-process)
  - [Communication Between Chatbot and Service Registry](#communication-between-chatbot-and-service-registry)
    - [**Chatbot Requesting Available Services**](#chatbot-requesting-available-services)
    - [**Chatbot Forwarding a Message to a Registered Service**](#chatbot-forwarding-a-message-to-a-registered-service)
  - [Running Other Services](#running-other-services)
    - [Running the Grammar Service](#running-the-grammar-service)
    - [Running the Django Chatbot](#running-the-django-chatbot)
  - [Conclusion](#conclusion)

---

## Prerequisites
Before running the project, ensure you have the following installed:
- **Python 3.8.10**
- **pip** (Python package manager)
- **Docker** (for containerized deployment)
- **Ollama** (for the AI interaction)

Ensure:
- **Ollama is running on your machine** (`http://localhost:11434`)

## Assignment 1: Running the Project Locally

#### 1️⃣ Clone the Repository
```sh
git clone https://github.com/Hasan-Saju/LLM-Project-Studio
cd LLM-Project-Studio
```

#### 2️⃣ Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate   # For macOS/Linux
venv\Scripts\activate     # For Windows
```

#### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

#### 4️⃣ Run Migrations
```sh
cd llm_project
python manage.py makemigrations
python manage.py migrate
```

#### 5️⃣ Start the Django Server
```sh
python manage.py runserver
```
- The application will be available at **http://127.0.0.1:8000/**

## Running the Project with Docker

#### 1️⃣ Build the Docker Image
```sh
docker build -t my-django-app .
```

#### 2️⃣ Run the Container
```sh
docker run -p 8000:8000 my-django-app
```
- The application will be accessible at **http://localhost:8000/**

## Environment Variables
To configure **Ollama API URL**, create a `.env` file in the `llm_project` directory with:
```env
ENVIRONMENT=development  # or 'production'
# Ollama API URL
OLLAMA_API_DEV=http://localhost:11434
OLLAMA_API_PROD=http://host.docker.internal:11434  
```

## Preview
![alt text](image.png)

# Assignment 2: Service Discovery
![alt text](ServiceRegistry.png)

## Service Registry - Microservices Discovery and Communication

## Overview
The **Service Registry** is a microservice that allows dynamic discovery, registration, and communication between different microservices in a distributed architecture. It enables microservices to register themselves, send heartbeats to indicate their availability, and communicate with each other.

## Features

- **Service Registration:** Microservices register themselves with the registry upon startup.
- **Heartbeat Monitoring:** Services send a heartbeat every 2 minutes to indicate they are alive.
- **Service Discovery:** Any service can request a list of available services.
- **Message Forwarding:** Allows a service to send a message to another service.
- **Auto Deregistration:** If a service fails to send a heartbeat within 5 minutes, it is removed from the registry.

## Technologies Used

- **Python** (Flask for the Service Registry, Requests for HTTP communication)
- **Django** (For the chatbot)
- **Threading** (For background monitoring of inactive services)

## Running the Service Registry
Run the service registry to allow microservices to register:
```bash
python service_registrar.py
```

## API Endpoints

### 1. Register a Service
- **Endpoint:** `POST /register`
- **Request Body:**
  ```json
  {
    "service_name": "grammar_service",
    "service_address": "http://localhost:5002/process"
  }
  ```
- **Response:**
  ```json
  {"message": "Service grammar_service registered successfully"}
  ```

### 2. List All Services
- **Endpoint:** `GET /list`
- **Response:**
  ```json
  {
    "grammar_service": "http://localhost:5002/process"
  }
  ```

### 3. Send Heartbeat
- **Endpoint:** `POST /heartbeat`
- **Request Body:**
  ```json
  {"service_name": "grammar_service"}
  ```
- **Response:**
  ```json
  {"message": "Heartbeat received from grammar_service"}
  ```

### 4. Forward a Message to Another Service
- **Endpoint:** `POST /forward`
- **Request Body:**
  ```json
  {
    "target_service": "grammar_service",
    "payload": {"message": "r u fine"}
  }
  ```
- **Response:**
  ```json
  {"fixed_message": "are you fine"}
  ```

## Service Cleanup Process
- A **background thread** runs every 60 seconds to check for inactive services.
- If a service does not send a heartbeat for **5 minutes**, it is automatically removed.

## Communication Between Chatbot and Service Registry

### **Chatbot Requesting Available Services**
- **Endpoint:** `GET /microservices/list/`
- **Chatbot Request:**
  ```python
  response = requests.get("http://localhost:5001/list")
  available_services = response.json()
  ```
- **Example Response:**
  ```json
  {
    "grammar_service": "http://localhost:5002/process"
  }
  ```

### **Chatbot Forwarding a Message to a Registered Service**
- **Endpoint:** `POST /microservices/forward/`
- **Chatbot Request:**
  ```python
  response = requests.post("http://localhost:5001/forward", json={
      "target_service": "grammar_service",
      "payload": {"message": "r u fine"}
  })
  fixed_message = response.json()["fixed_message"]
  ```
- **Example Response:**
  ```json
  {"fixed_message": "are you fine"}
  ```

## Running Other Services

### Running the Grammar Service
```bash
python grammar_service.py
```

### Running the Django Chatbot
```bash
python manage.py runserver
```

## Conclusion
The **Service Registry** ensures seamless communication between microservices by dynamically managing service discovery and request forwarding.

