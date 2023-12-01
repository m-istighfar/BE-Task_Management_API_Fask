# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the relevant files and directories from your project folder to the Docker container
COPY ./src /app

# Install Pipenv
RUN pip install -U pipenv

# Install dependencies using Pipenv
RUN pipenv install --deploy

# Expose port 80 for Gunicorn
EXPOSE 80

# Run Gunicorn
CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:80", "app:app"]
