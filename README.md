# LLM Project Studio

Welcome to the LLM Project Studio! This is a Django-based project that integrates with Ollama. The project is containerized using Docker for easy deployment.

## Prerequisites
Before running the project, ensure you have the following installed:
- **Python 3.8.10**
- **pip** (Python package manager)
- **Docker** (for containerized deployment)
- **Ollama** (for the AI interaction)

ensure:
- **Ollama is running on your machine** (`http://localhost:11434`)

<br>

## Running the Project Locally

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


<br>

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


<br>


## Environment Variables
To configure **Ollama API URL**, create a `.env` file in the `llm_project` directory with:
```env
ENVIRONMENT=development  # or 'production'
# Ollama API URL
OLLAMA_API_DEV=http://localhost:11434
OLLAMA_API_PROD=http://host.docker.internal:11434  
```

<br>

## Preview
![alt text](image.png)



## Preview
![alt text](ServiceRegistry.png)


