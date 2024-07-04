# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /root

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy the config.yml from the GitHub Secrets during build time
ARG CONFIG_YML
RUN echo "${CONFIG_YML}" > /root/config.yml

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]