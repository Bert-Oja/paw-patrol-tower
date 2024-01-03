# Use Python 3.11 Alpine base image
FROM python:3.11.2-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies and clean up in one layer
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/cache/apk/*

# Copy the content of the local src directory to the working directory
COPY ./src .

# Install ffmpeg
RUN apk add --no-cache ffmpeg

# Expose the port 8000
EXPOSE 8000

# Run the app with gunicorn
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000"]