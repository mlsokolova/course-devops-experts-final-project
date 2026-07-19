# AI Handoff

## Context
- Project: `final-project` (QuakeWatch + DuckDB/Quack)
- Current phase: Docker, Kubernetes, Helm, GitHub Actions, and Argo CD GitOps
- Next tasks:
  - add a merged-PR guard to `.github/workflows/main-merge.yaml`
  - validate the Helm chart and GitHub Actions in the target environment
  - continue with the infrastructure and analytics work in `TODO.md`

## Architecture Snapshot
- `quakewatch` (Flask app) calls:
  - USGS API for live graph/event data
  - `duckdb` service over Quack (`QUACK__HOST` / `QUACK__PORT`) for historical stats
- `duckdb` service:
  - Runs `duckdb-quack-service.py`
  - Uses PVC-mounted database file (`DUCKDB__PATH`)
  - Seeded by init container running `seed_data.py`
- Argo CD:
  - Monitors the `helm/` directory in the `main` branch
  - Treats the Helm chart in `main` as the deployment source of truth
  - Does not have application manifests stored in this repository

## What Was Completed
- Split raw Kubernetes resources into the `kubernetes/` folder.
- Added and updated manifests:
  - `kubernetes/quakewatch.yaml`
  - `kubernetes/duckdb.yaml`
  - `kubernetes/configmap-quakewatch.yaml`
  - `kubernetes/secret-quakewatch.yaml`
  - `kubernetes/pv-duckdb.yaml`
  - `kubernetes/hpa-quakewatch.yaml`
  - `kubernetes/cronjob-quakewath-check.yaml`
  - `kubernetes/components.yaml`
- Created a Helm chart in `helm/` that packages the Kubernetes resources:
  - `Chart.yaml`, `values.yaml`, `_helpers.tpl`
  - templates for app/data Deployments and Services, ConfigMap/Secret, PV/PVC, HPA, CronJob, metrics-server, and a test pod
- Improved Helm Secret token behavior:
  - `secret.quackToken: ""` by default
  - auto-generates on first install (`randAlphaNum 32`)
  - reuses the existing Secret token on upgrade via `lookup` to avoid rotation
- Removed default Helm scaffold leftovers:
  - deleted `deployment.yaml`, `service.yaml`, `serviceaccount.yaml`, `ingress.yaml`, `httproute.yaml`
- Updated docs:
  - `README.md`
  - `docs/1-Docker.md`
  - `docs/2-Kubernetes.md`
  - `docs/3-Helm.md`
  - `docs/4-Branching-Strategy.md`
- Merged prior DuckDB usage notes into `README.md` and removed separate `duckdb-usage.md`.
- Added historical analytics to `QuakeStats`:
  - median magnitude and average time between earthquakes
  - highest-magnitude earthquake
  - average earthquake count per day
  - day with the highest earthquake count
  - combined JSON result exposed as `QuakeStats.all_stats`
- Updated the graph dashboard to display the combined historical statistics.
- Added GitHub Actions workflows:
  - `.github/workflows/push-branch.yaml` runs Pylint and builds the image for non-`main` pushes that change `Quakewatch/**` or `Dockerfile`
  - `.github/workflows/main-merge.yaml` builds and pushes a Docker image when a pull request into `main` is closed and changes `Quakewatch/**` or `Dockerfile`
- Defined the semantic-version branching and release process in `docs/4-Branching-Strategy.md`.

## Important Operational Notes
- Use either raw manifests (`kubernetes/`) or Helm (`helm/`) per environment; do not deploy both into the same namespace.
- The Helm chart in `main` is synchronized by Argo CD. Keep it valid and deployable.
- Helm-only changes do not trigger a Docker image build. This is expected when application files and `Dockerfile` are unchanged.
- Version branch names become Docker image tags and must be valid Docker tags (for example, `3.3.1`; do not use `/`).
- If application code changes, update `helm/values.yaml` to reference the image tag created from the version branch.
- Avoid manual changes to Argo CD-managed Kubernetes resources because Argo CD may revert them.
- Helm test hook exists at `helm/templates/tests/test-connection.yaml`.
  - Runs only with `helm test <release> -n <namespace>`.
- `metricsServer.enabled` is `false` by default in `helm/values.yaml`.
- `kubernetes/components.yaml` and the Helm Metrics Server template contain cluster-wide (`kube-system`) resources.

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
- Metrics Server installation is optional and cluster-scoped.
- The Helm CLI was not available in this environment during chart rendering validation, so a final `helm template` check should be run in the target environment.
- `.github/workflows/main-merge.yaml` listens for closed pull requests but does not currently check `github.event.pull_request.merged == true`; closing an unmerged matching pull request can publish an image.
- Image versions are not fully synchronized: `helm/Chart.yaml` has `appVersion: "3.2.0"`, while `helm/values.yaml` uses image tag `3.3.1`, and some raw manifests and documentation still reference `3.2.0`.
- The workflows run only when `Quakewatch/**` or `Dockerfile` changes. Changes elsewhere do not trigger those workflows.

## First Message for New Chat (Copy/Paste)
Use `HANDOFF.md` in this repo as the source of truth, then:
1) add a merged-only condition to `.github/workflows/main-merge.yaml`,
2) reconcile image versions across Helm, raw manifests, and documentation,
3) validate Helm rendering and the Argo CD synchronization path,
4) continue with the remaining items in `TODO.md`.
