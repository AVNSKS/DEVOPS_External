# Use an official, lightweight Python run environment
FROM python:3.11-slim

# Set internal path variables
WORKDIR /app

# Install critical web server requirements
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Copy our service code directly into the workspace
COPY main.py /app/main.py

# Expose the API container execution port
EXPOSE 8000

# Fire up the high-performance ASGI server engine
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]