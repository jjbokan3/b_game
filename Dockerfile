# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install jp2a
RUN apt-get update && apt-get install -y jp2a

# Make port 80 available to the world outside this container (if you need to expose any ports)
EXPOSE 80

# Run game.py when the container launches
# CMD ["python", "user_interface.py"]

