#FROM ubuntu:latest
#LABEL authors="daiji"
#
#ENTRYPOINT ["top", "-b"]

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is sent directly to the terminal
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Django port
EXPOSE 8000

# Start Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# al momento di deployment, runserver viene sotituito da Gunicorn