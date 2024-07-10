# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY flask_app/requirements.txt /app/

# Install required apt packes
RUN apt update && apt install pkg-config default-libmysqlclient-dev gcc -y


# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app
COPY flask_app /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=server.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
