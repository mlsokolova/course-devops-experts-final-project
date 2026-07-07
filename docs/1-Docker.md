# Phase 1: Foundation — Docker

This folder contains Docker resources for the [QuakeWatch](https://github.com/EduardUsatchev/QuakeWatch) Flask application: **Dockerfile**, **docker-compose.yml**, and this **README**.

Application source lives in **`Quakewatch/`** (vendored copy of the upstream repo). The image is built from the official **`python:3.11-slim`** base image: dependencies are installed from `Quakewatch/requirements.txt`, then the app files are copied into the container.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- Optional: [Docker Compose](https://docs.docker.com/compose/install/) v2

## Build the image

From the directory (`final-project`):

```bash
docker build -t mlsokolova/quakewatch .
```

## Run with Docker

```bash
docker run --rm -p 5000:5000 mlsokolova/quakewatch
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

The app needs outbound **HTTPS** to reach the USGS API.

## Run with Docker Compose

```bash
docker compose up --build
```

Open [http://localhost:5000](http://localhost:5000).

Compose builds the same image, maps port **5000**, and mounts a **`tmpfs`** on `Quakewatch/logs` so the app can write log files.

## Push to Docker Hub  
```
docker tag mlsokolova/quakewatch mlsokolova/quakewatch:3.2.0
docker push mlsokolova/quakewatch:3.2.0
```

## Project layout

| Path | Purpose |
| ---- | ------- |
| `Quakewatch/` | Flask application (Python source, templates, static files) |
| `Dockerfile` | Builds the image: install requirements, copy `Quakewatch/` |
| `docker-compose.yml` | Runs the container locally |
