# AI Handoff

## Context
- Project: `final-project` (QuakeWatch + DuckDB/Quack)
- Current phase: Docker + Kubernetes manifests + Helm chart
- Next task: implement github actions

## Architecture Snapshot
- `quakewatch` (Flask app) calls:
  - USGS API for live graph/event data
  - `duckdb` service over Quack (`QUACK__HOST` / `QUACK__PORT`) for historical stats
- `duckdb` service:
  - Runs `duckdb-quack-service.py`
  - Uses PVC-mounted database file (`DUCKDB__PATH`)
  - Seeded by init container running `seed_data.py`

## What Was Completed
- Split raw Kubernetes resources into `kubernetes/` folder.
- Added and updated manifests:
  - `kubernetes/quakewatch.yaml`
  - `kubernetes/duckdb.yaml`
  - `kubernetes/configmap-quakewatch.yaml`
  - `kubernetes/secret-quakewatch.yaml`
  - `kubernetes/pv-duckdb.yaml`
  - `kubernetes/hpa-quakewatch.yaml`
  - `kubernetes/cronjob-quakewath-check.yaml`
  - `kubernetes/components.yaml`
- Standardized image tag usage to `mlsokolova/quakewatch:3.2.0` across manifests/docs/compose.
- Created Helm chart in `helm/` that implements kubernetes resources:
  - `Chart.yaml`, `values.yaml`, `_helpers.tpl`
  - templates for app/data deployments and services, configmap/secret, pv/pvc, hpa, cronjob, metrics-server, test pod
- Helm secret token behavior improved:
  - `secret.quackToken: ""` by default
  - auto-generate on first install (`randAlphaNum 32`)
  - reuse existing Secret token on upgrade via `lookup` to avoid rotation
- Removed default Helm scaffold leftovers:
  - deleted `deployment.yaml`, `service.yaml`, `serviceaccount.yaml`, `ingress.yaml`, `httproute.yaml`
- Updated docs:
  - `README.md`
  - `docs/2-Kubernetes.md`
  - `docs/3-Helm.md`
- Merged prior DuckDB usage notes into `README.md` and removed separate `duckdb-usage.md`.

## Important Operational Notes
- Use either raw manifests (`kubernetes/`) or Helm (`helm/`) per environment; do not deploy both into same namespace.
- Helm test hook exists at `helm/templates/tests/test-connection.yaml`.
  - Runs only with `helm test <release> -n <namespace>`.
- `metricsServer.enabled` is `false` by default in `helm/values.yaml`.
- `kubernetes/components.yaml` / Helm metrics-server template are cluster-wide (`kube-system`) resources.

## Key Commands
- Helm install:
  - `helm install quakewatch ./helm -n final-project --create-namespace`
- Helm upgrade:
  - `helm upgrade quakewatch ./helm -n final-project`
- Helm test:
  - `helm test quakewatch -n final-project`
- Raw manifests apply:
  - `kubectl apply -f kubernetes/configmap-quakewatch.yaml`
  - `kubectl apply -f kubernetes/secret-quakewatch.yaml`
  - `kubectl apply -f kubernetes/pv-duckdb.yaml`
  - `kubectl apply -f kubernetes/duckdb.yaml`
  - `kubectl apply -f kubernetes/quakewatch.yaml`


## Known Caveats
- `hostPath` PV is environment-sensitive (especially local Docker Desktop paths).
- Metrics server install is optional and cluster-scoped.
- Helm CLI was not available in this environment during chart render validation, so final `helm template` check should be run in target environment.

## First Message for New Chat (Copy/Paste)
Use `HANDOFF.md` in this repo as the source of truth, then:
1) validate Helm chart rendering/install in the new repo,
2) verify docs and paths after migration,
3) continue with remaining analytics TODOs.
