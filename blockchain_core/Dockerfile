# Use an official Python runtime as a parent image
FROM python:3.5-slim

# Set the working directory to /app
WORKDIR /app

COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
# CMD ["python", "flask_app.py"]
