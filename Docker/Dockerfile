# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

ARG PORT
ENV PORT=${PORT}
ARG HOST
ENV HOST=${HOST}


# Expose the port the app runs on
EXPOSE ${PORT}

# Command to run the FastAPI application
# CMD ["python", "src/agent.py", "--host", "${HOST}", "--port", "${PORT}"]
CMD ["sh", "-c", "python src/agent.py --port $PORT"]
# CMD ["tail", "-f", "/dev/null"]
