# GitHub Actions Workflows

## Overview

The project uses GitHub Actions to validate application changes and publish versioned Docker images.

| Workflow | Purpose |
| -------- | ------- |
| `.github/workflows/push-branch.yaml` | Runs Pylint and verifies that the Docker image builds on version branches |
| `.github/workflows/main-merge.yaml` | Builds and pushes a versioned Docker image after a matching pull request into `main` is closed |

The branching and release conventions used by these workflows are described in [4-Branching-Strategy.md](4-Branching-Strategy.md).

## Path filters

Both workflows run only when a matching change affects:

```text
Quakewatch/**
Dockerfile
```

`Quakewatch/**` matches files in the application directory and all its subdirectories. The filter applies to added, modified, and deleted files.

Changes limited to documentation, raw Kubernetes manifests, or `helm/` do not trigger these workflows. Helm-only changes do not require a new application image and are synchronized separately by Argo CD after they reach `main`.

## Branch validation workflow

File: `.github/workflows/push-branch.yaml`

### Trigger

The workflow runs on pushes to every branch except `main`, provided that at least one changed file matches the path filters.

### Job

The `check-and-build` job runs on `ubuntu-latest` and performs these steps:

1. Checks out the repository with `actions/checkout@v6`.
2. Installs Python 3.11 with `actions/setup-python@v5`.
3. Installs the dependencies from `Quakewatch/requirements.txt`.
4. Installs Pylint.
5. Runs Pylint against the Python files in `Quakewatch/`.
6. Builds the Docker image.

This workflow does not push the image to Docker Hub. Its purpose is to detect lint, dependency, and image-build failures before a branch is merged.

### Equivalent local checks

Run these commands from the repository root:

```bash
pip install -r Quakewatch/requirements.txt
pip install pylint
pylint Quakewatch/*.py
docker build -t mlsokolova/quakewatch .
```

## Main merge workflow

File: `.github/workflows/main-merge.yaml`

### Trigger

The workflow listens for pull requests into `main` with the `closed` event. It runs only when at least one changed file matches the path filters.

### Job

The `build-and-push-docker-image` job runs on `ubuntu-latest` and performs these steps:

1. Checks out the repository with `actions/checkout@v6`.
2. Builds the Docker image.
3. Tags the image with the pull request source branch name.
4. Logs in to Docker Hub.
5. Pushes the image to Docker Hub.

For example, closing a matching pull request from branch `3.3.1` produces:

```text
mlsokolova/quakewatch:3.3.1
```

Version branch names must be valid Docker tags. Use semantic versions such as `3.3.1`; names containing `/` are incompatible with the current tagging command.

## Required GitHub configuration

Configure these values in the GitHub repository under **Settings → Secrets and variables → Actions**:

| Type | Name | Purpose |
| ---- | ---- | ------- |
| Repository variable | `DOCKERHUB_USERNAME` | Docker Hub account or organization name |
| Repository secret | `DOCKERHUB_TOKEN` | Docker Hub access token with permission to push images |

The workflow publishes images to:

```text
${DOCKERHUB_USERNAME}/quakewatch:<version-branch>
```

Use a Docker Hub access token instead of an account password. Never store the token directly in a workflow or commit it to the repository.

## Important merge guard

The `closed` pull-request event also fires when a pull request is closed without being merged. The current workflow does not distinguish that case.

Add a job condition to ensure that only merged pull requests publish an image:

```yaml
jobs:
  build-and-push-docker-image:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
```

Without this condition, closing an unmerged pull request that matches the path filters can build and publish an image.

## Argo CD relationship

Argo CD monitors the `helm/` directory in the `main` branch.

The application release flow is:

1. A version branch is validated by `push-branch.yaml`.
2. The Helm image tag is updated to the version branch name when the application image changes.
3. The pull request is reviewed and merged into `main`.
4. `main-merge.yaml` builds and publishes the versioned image.
5. Argo CD detects the Helm change in `main` and synchronizes the Kubernetes deployment.

The image referenced by `helm/values.yaml` must exist in Docker Hub before the deployment can become healthy.

## Troubleshooting

### Workflow does not start

Verify that:

- the changed file is under `Quakewatch/` or is the root `Dockerfile`;
- the branch or pull-request target matches the workflow trigger;
- GitHub Actions is enabled for the repository;
- the workflow file is under `.github/workflows/`.

### Docker Hub login fails

Verify that `DOCKERHUB_USERNAME` exists as a repository variable and `DOCKERHUB_TOKEN` exists as a repository secret. Confirm that the token has permission to push to the `quakewatch` repository.

### Docker tag is invalid

Use a semantic-version branch name such as `3.3.1`. Do not use a branch name containing `/` because the source branch name is inserted directly into the Docker tag.

### Argo CD reports an image pull error

Confirm that:

- `helm/values.yaml` references the expected image tag;
- the image exists in Docker Hub;
- the Kubernetes cluster can access the Docker Hub repository;
- any required image-pull secret is configured.
