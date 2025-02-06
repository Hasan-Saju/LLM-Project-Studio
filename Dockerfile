FROM python:3.8.10
WORKDIR /app/llm_project
COPY . /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose port 8000 for Django
EXPOSE 8000

# Set environment variables for production
ENV ENVIRONMENT=production

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
