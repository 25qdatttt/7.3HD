# Jenkins Custom Image (with Docker CLI)

This folder contains a custom Dockerfile for building a Jenkins image that includes:
- Docker CLI
- Docker Compose

## Why?
The default Jenkins image does not include Docker, which causes "permission denied" errors when the pipeline tries to run `docker build`.  
By creating a custom Jenkins image, the pipeline can build, test, and deploy Docker containers seamlessly.

## Build and Run

```bash
# Build the custom Jenkins image
docker build -t jenkins-docker .

# Run Jenkins with mounted Docker socket
docker run -d --name jenkins -u root -p 8080:8080 -p 50000:50000 ^
    -v jenkins_home:/var/jenkins_home ^
    -v /var/run/docker.sock:/var/run/docker.sock ^
    jenkins-docker
