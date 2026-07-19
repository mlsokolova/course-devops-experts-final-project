# Branching Strategy

## Overview

This project uses `main` as its stable branch and version branches for development and releases. Changes are reviewed through pull requests before they are merged into `main`.

The `helm/` directory in `main` is the source of truth for Argo CD. Therefore, `main` must always contain a valid and deployable Helm chart.

## Branches

### `main`

The `main` branch contains the current stable version of the application and its deployment configuration.

- Changes should be merged through pull requests rather than committed directly.
- Required CI checks should pass before a pull request is merged.
- The Helm chart in `main` is automatically synchronized by Argo CD.
- Force pushes and branch deletion should be disabled.

### Version branches

Create a version branch for each release using semantic versioning:

```text
MAJOR.MINOR.PATCH
```

Examples:

```text
3.3.1
3.4.0
4.0.0
```

The branch name is also used as the Docker image tag. For example, merging branch `3.3.1` produces:

```text
mlsokolova/quakewatch:3.3.1
```

Branch names must therefore be valid Docker tags. Names containing `/`, such as `feature/dashboard`, are not compatible with the current image-tagging workflow.

## Development and release workflow

1. Update the local `main` branch.
2. Create a version branch.
3. Implement and test the changes.
4. If the application image changes, update the image tag in the Helm values to match the version branch.
5. Push the branch to GitHub.
6. Open a pull request into `main`.
7. Wait for CI checks and review.
8. Merge the pull request.
9. Verify that the Docker image was published.
10. Verify that Argo CD synchronized the Helm chart successfully.

Example:

```bash
git switch main
git pull
git switch -c 3.3.1

# Make and commit changes
git add .
git commit -m "Add earthquake statistics"
git push -u origin 3.3.1
```

## Continuous integration

For pushes to branches other than `main`, `.github/workflows/push-branch.yaml`:

- installs the Python dependencies;
- runs Pylint;
- builds the Docker image.

When a pull request into `main` is merged, `.github/workflows/main-merge.yaml`:

- builds the Docker image;
- uses the source branch name as the image tag;
- pushes the image to Docker Hub.

The merge workflow must run only for merged pull requests. A pull request that is closed without being merged must not publish an image.

## Argo CD deployment

Argo CD monitors the `helm/` directory in the `main` branch.

- Helm changes on version branches are not deployed.
- Merging Helm changes into `main` makes them available to Argo CD.
- Argo CD synchronizes the Kubernetes environment with the Helm chart in `main`.
- Manual changes to Argo CD-managed Kubernetes resources should be avoided because Argo CD may revert them.
- The Docker image referenced by the Helm chart must exist before the deployment can become healthy.

## Recommended branch protection

Configure the following protection rules for `main`:

- Require a pull request before merging.
- Require CI checks to pass.
- Require at least one approval.
- Prevent force pushes.
- Prevent branch deletion.

