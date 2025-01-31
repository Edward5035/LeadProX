# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Firefox and related dependencies
RUN apt-get update && apt-get install -y wget gnupg \
    && apt-get install -y firefox-esr

# Run the application
CMD ["gunicorn", "app:app", "-t", "240", "--keep-alive", "120"]
