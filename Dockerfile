# FROM python:3.9-alpine
# WORKDIR /
# COPY requirements.txt ./
# RUN pip install -r requirements.txt
# COPY . .
# EXPOSE 5000
# CMD ["cd llm_project", "python", "manage.py makemigrations", "python", "manage.py migrate", "python", "manage.py runserver"]

# FROM python:3.9-alpine
# WORKDIR /LLM_project
# COPY requirements.txt ./
# RUN pip install -r requirements.txt
# COPY . .
# # WORKDIR /LLM_project/llm_project
# EXPOSE 8000
# CMD ["sh", "-c", "cd llm_project && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
# CMD ["sh", "-c", "cd llm_project && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# Use an official Python runtime as a parent image
FROM python:3.8.10

WORKDIR /app/llm_project

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose port 8000 for Django
EXPOSE 8000


# Set environment variables for production
ENV ENVIRONMENT=production

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
