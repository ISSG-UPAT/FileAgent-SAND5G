# FileAgent Dockerimage

## Functionality

### Variables

| Variable  | Required | Default Values | Description                                  |
| --------- | -------- | -------------- | -------------------------------------------- |
| PORT      | OPTIONAL | 8000           | The port on which the FileAgent will run.    |
| HOST      | OPTIONAL | "0.0.0.0"      | The host on which the FileAgent will run.    |
| DIRECTORY | OPTIONAL | <>             | The directory to be monitored.               |
|           |          |                | Defaults to the parent directory of the file |
| FILE      | YES      |                | The file to be monitored.                    |

### Docker compose

```yaml
services:
  fileagent:
    image: issgupat/fileagent-docker-sand5g:latest
    environment:
      - PORT=8000
      - HOST="0.0.0.0"
      - FILE=<name of your file>
      - DIRECTORY=/app/custom
    hostname: fileagent
    network_mode: "host"
    ports:
      - "8000:8000"
    volumes:
      - custom_data:/app/custom

volumes:
  custom_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/your/custom
```

## Makefile

```
docker-build         Build the Docker image."
docker-delete        Delete the Docker image."
docker-push          Push the Docker image to Docker Hub."
help                 Show this help message."
```
