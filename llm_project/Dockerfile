FROM python:3.9-alpine
WORKDIR /llm_project
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "manage.py makemigrations", "python", "manage.py migrate", "python", "manage.py runserver"]
