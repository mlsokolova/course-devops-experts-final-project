# Phase 3: Packaging — Helm

Helm chart in [`helm/`](../helm/) packages the manifests from [`kubernetes/`](../kubernetes/) as a single installable release.

Image: `mlsokolova/quakewatch:3.2.0` (namespace `final-project`).

## Prerequisites

- [Helm 3](https://helm.sh/docs/intro/install/)
- Kubernetes cluster with `kubectl` configured
- Namespace `final-project` (created automatically with `--create-namespace`)

## Install

From the `final-project` directory:

```bash
helm install quakewatch ./helm -n final-project --create-namespace
```

Optional components (disabled by default in `values.yaml`):

```bash
# metrics-server for HPA (cluster-wide, kube-system)
helm install quakewatch ./helm -n final-project --create-namespace \
  --set metricsServer.enabled=true
```

## Upgrade

```bash
helm upgrade quakewatch ./helm -n final-project
```

Override common settings:

```bash
helm upgrade quakewatch ./helm -n final-project \
  --set image.tag=3.2.0 \
  --set secret.quackToken=my-secret-token \
  --set persistence.pv.hostPath=/data/duckdb
```

## Verify

```bash
helm status quakewatch -n final-project
kubectl get pods -n final-project
kubectl get svc -n final-project
```

Port-forward the web app:

```bash
kubectl port-forward svc/quakewatch 5000:5000 -n final-project
```

Visit [http://127.0.0.1:5000/graph-earthquakes](http://127.0.0.1:5000/graph-earthquakes).

## Uninstall

```bash
helm uninstall quakewatch -n final-project
```

PersistentVolume with `Retain` policy is not removed automatically. Delete manually if needed:

```bash
kubectl delete pv duckdb-data
```

## Chart contents

| Template | Kubernetes resource |
| -------- | --------------------- |
| `configmap.yaml` | ConfigMap |
| `secret.yaml` | Secret |
| `pv-duckdb.yaml` | PersistentVolume (optional) |
| `pvc-duckdb.yaml` | PersistentVolumeClaim |
| `duckdb-deployment.yaml` | Deployment (`duckdb`) |
| `duckdb-service.yaml` | Service (`duckdb`) |
| `quakewatch-deployment.yaml` | Deployment (`quakewatch`) |
| `quakewatch-service.yaml` | Service (`quakewatch`) |
| `hpa.yaml` | HorizontalPodAutoscaler |
| `cronjob.yaml` | CronJob |
| `metrics-server.yaml` | metrics-server (optional, `kube-system`) |

Configure defaults in [`helm/values.yaml`](../helm/values.yaml).

## Render templates locally

```bash
helm template quakewatch ./helm -n final-project
```

## Relation to `kubernetes/`

The flat manifests in `kubernetes/` remain available for step-by-step learning (see [2-Kubernetes.md](2-Kubernetes.md)). The Helm chart is equivalent for deployment; prefer one approach per environment to avoid duplicate resources.

## Pack and publish to the Docker Hub artifact repository 
```
helm package ./helm
helm push quakewatch-0.1.0.tgz oci://registry-1.docker.io/mlsokolova
```
## Install from Docker Hub  
```
helm upgrade -i quakewatch oci://registry-1.docker.io/mlsokolova/quakewatch --version 0.1.0 --set metricsServer.enabled=true
``