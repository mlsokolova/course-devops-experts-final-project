# Phase 2: Orchestration — Kubernetes Basics & Advanced

This phase deploys the customized QuakeWatch stack on Kubernetes: the Flask web app (`quakewatch`) and the DuckDB Quack server (`duckdb`). The web app queries USGS for live graphs and uses `quakestats.py` to fetch historical statistics from DuckDB over the Quack protocol.

Image: `mlsokolova/quakewatch:3.2.0` (namespace `final-project`).

All manifests live in the [`kubernetes/`](../kubernetes/) folder. Run `kubectl` commands below from the `final-project` directory.

## Set up the cluster

```bash
kubectl create ns final-project
kubectl config set-context --current --namespace=final-project
```

## Run the dockerized web app as a pod (optional smoke test)

```bash
docker pull mlsokolova/quakewatch:3.2.0
kubectl run quakewatch --image=mlsokolova/quakewatch:3.2.0
```

This runs only the Flask container without DuckDB. Pages that depend on `QuakeStats` (for example `/graph-earthquakes`) need the full stack below.

## Deploy configuration and storage

Apply shared config before the workloads:

```bash
kubectl apply -f kubernetes/configmap-quakewatch.yaml
kubectl apply -f kubernetes/secret-quakewatch.yaml
kubectl apply -f kubernetes/pv-duckdb.yaml
```

| Manifest | Kind | Purpose |
| -------- | ---- | ------- |
| `kubernetes/configmap-quakewatch.yaml` | ConfigMap | `QUAKEWATCH__LOG_PATH`, `MPLCONFIGDIR`, `QUACK__HOST`, `QUACK__PORT`, `DUCKDB__PATH` |
| `kubernetes/secret-quakewatch.yaml` | Secret | `QUACK__TOKEN` (shared by `quakewatch` and `duckdb`) |
| `kubernetes/pv-duckdb.yaml` | PV + PVC | Persistent storage for `/data/earthquakes.duckdb` |

The PVC `duckdb-data` uses a `hostPath` volume at `/data/duckdb` on the node. On Docker Desktop you may need to copy `seed-data/` there, or adjust the `hostPath` in `kubernetes/pv-duckdb.yaml` to point at your local folder.

## Deploy DuckDB

```bash
kubectl apply -f kubernetes/duckdb.yaml
```

The `duckdb` Deployment includes:

- **init container** `seed-data` — runs `seed_data.py`; downloads the parquet file and creates the `earthquakes` table if missing
- **main container** — runs `duckdb-quack-service.py`; serves Quack on port `9494`

Wait until the pod is ready:

```bash
kubectl get pods -l app=duckdb
kubectl logs -l app=duckdb -c seed-data
```

## Deploy QuakeWatch

```bash
kubectl apply -f kubernetes/quakewatch.yaml
```

The `quakewatch` Deployment includes:

- **init container** `wait-for-duckdb` — blocks until the `duckdb` Service is reachable on the Quack port
- **main container** — runs `app.py`; env vars for logging, matplotlib, and Quack connectivity come from the ConfigMap and Secret

Verify both services:

```bash
kubectl get pods
kubectl get svc
```

Open the app via the `quakewatch` NodePort or port-forward:

```bash
kubectl port-forward svc/quakewatch 5000:5000
```

Then visit [http://127.0.0.1:5000/graph-earthquakes](http://127.0.0.1:5000/graph-earthquakes).

## Run the CronJob

```bash
kubectl apply -f kubernetes/cronjob-quakewath-check.yaml
```

Periodic health check via `curl` to `/graph-earthquakes` (exercises both Flask and DuckDB).

## Install Metrics Server

1. Download the upstream manifest (optional — a patched copy is already in the repo):

   ```bash
   wget https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.8.1/components.yaml
   ```

2. For local clusters (Docker Desktop), add `--kubelet-insecure-tls` to the container `args` section. [`kubernetes/components.yaml`](../kubernetes/components.yaml) already includes this flag.

3. Apply:

   ```bash
   kubectl apply -f kubernetes/components.yaml
   ```

4. Wait a minute, then check:

   ```bash
   kubectl top node
   ```

   Expected output:

   ```
   NAME                    CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
   desktop-control-plane   128m         0%       783Mi           5%
   desktop-worker          31m          0%       607Mi           3%
   ```

## Apply Horizontal Pod Autoscaler

```bash
kubectl apply -f kubernetes/hpa-quakewatch.yaml
```

## Test Horizontal Pod Autoscaler

1. Run the Apache HTTP server benchmarking tool:

   ```bash
   kubectl run quakewatch-benchmark -it --rm --restart=Never --image=httpd:2.4 -- ab -n 100 -c 20 -s 60 http://quakewatch:5000/graph-earthquakes
   ```

   (100 requests to the heaviest page, 20 in parallel.)

2. Watch scaling events:

   ```bash
   kubectl get events
   kubectl get hpa
   ```

## Manifest overview

| File | Resources |
| ---- | --------- |
| `kubernetes/configmap-quakewatch.yaml` | ConfigMap |
| `kubernetes/secret-quakewatch.yaml` | Secret |
| `kubernetes/pv-duckdb.yaml` | PersistentVolume, PersistentVolumeClaim |
| `kubernetes/duckdb.yaml` | Deployment, Service (`duckdb`) |
| `kubernetes/quakewatch.yaml` | Deployment, Service (`quakewatch`) |
| `kubernetes/cronjob-quakewath-check.yaml` | CronJob |
| `kubernetes/hpa-quakewatch.yaml` | HorizontalPodAutoscaler |
| `kubernetes/components.yaml` | metrics-server (cluster-wide) |

## Teardown

Delete resources in reverse order of deployment:

```bash
kubectl delete -f kubernetes/hpa-quakewatch.yaml
kubectl delete -f kubernetes/cronjob-quakewath-check.yaml
kubectl delete -f kubernetes/quakewatch.yaml
kubectl delete -f kubernetes/duckdb.yaml
kubectl delete -f kubernetes/pv-duckdb.yaml
kubectl delete -f kubernetes/secret-quakewatch.yaml
kubectl delete -f kubernetes/configmap-quakewatch.yaml
```
