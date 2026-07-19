# Phase 1: Foundation — Docker

This guide covers Docker resources for the [QuakeWatch](https://github.com/EduardUsatchev/QuakeWatch) Flask application: **Dockerfile**, **docker-compose.yml**, and related Compose setup.

Application source lives in **`Quakewatch/`** (vendored copy of the upstream repo). The image is built from the official **`python:3.11-slim`** base image: dependencies are installed from `Quakewatch/requirements.txt`, then the app files are copied into the container.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) v2

## Build the image

From the `final-project` directory:

```bash
docker build -t mlsokolova/quakewatch .
```

## Load seed data

```bash
docker run --volume ./seed-data:/data -e "DUCKDB__PATH=/data/earthquakes.duckdb" mlsokolova/quakewatch python seed_data.py
```

## Run with Docker Compose

```bash
docker compose up --build
```

Open [http://localhost:5000](http://localhost:5000).

Compose builds the same image, maps port **5000**, and mounts a **`tmpfs`** on `Quakewatch/logs` so the app can write log files.

## Push to Docker Hub

```bash
docker tag mlsokolova/quakewatch mlsokolova/quakewatch:3.3.1
docker push mlsokolova/quakewatch:3.3.1
```

## Project layout

| Path | Purpose |
| ---- | ------- |
| `Quakewatch/` | Flask application (Python source, templates, static files) |
| `Dockerfile` | Builds the image by installing requirements and copying `Quakewatch/` |
| `docker-compose.yml` | Runs `quakewatch` and `duckdb` locally |
