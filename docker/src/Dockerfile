# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

COPY ./volumes/scripts/entrypoint.sh . 

# Install the dependencies
RUN pip install --no-cache-dir fileagent
RUN chmod +x entrypoint.sh

ARG PORT
ENV PORT=${PORT}
ARG HOST
ENV HOST=${HOST}

ARG DIRECTORY
ENV DIRECTORY=${DIRECTORY}
ARG FILE
ENV FILE=${FILE}

# Expose the port the app runs on
EXPOSE ${PORT}

# Command to run the FastAPI application
# CMD ["python", "src/agent.py", "--host", "${HOST}", "--port", "${PORT}"]
# CMD ["sh", "-c", "/app/entrypoint.sh"]
# CMD ["tail","-f","/dev/null"]
CMD ["/app/entrypoint.sh"]