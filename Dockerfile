# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies needed for Python packages, document conversion, Tesseract OCR, spaCy, and Poppler for PDF processing
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libreoffice \
    poppler-utils \
    tesseract-ocr && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy language model
RUN python -m spacy download en_core_web_md

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port for FastAPI
EXPOSE 5001

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the FastAPI application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5001"]
