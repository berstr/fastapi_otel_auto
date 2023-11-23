# Use the official Python base image
FROM python:3.11.5-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose the port on which the application will run
EXPOSE 8000

# Run the FastAPI application using uvicorn server
CMD ["opentelemetry-instrument","--traces_exporter","console,otlp","--metrics_exporter","console,otlp","--logs_exporter","console,otlp", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]