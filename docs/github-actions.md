# GitHub Actions Workflow Documentation

This document describes the automated GitHub Actions workflow for building and publishing the File-Based Catalog (FBC).

## Workflow File

Location: `.github/workflows/build-catalog.yml`

## Trigger Conditions

The workflow runs when:

1. **Push to main branch** with changes to:
   - `catalog/**` - Any operator configuration changes
   - `.github/workflows/build-catalog.yml` - Workflow file changes
   - `scripts/generate-fbc.py` - Generator script changes

2. **Manual trigger** via `workflow_dispatch`

## Workflow Steps

### 1. Checkout Repository
```yaml
uses: actions/checkout@v4
```
Clones the repository with full history.

### 2. Set up Python
```yaml
uses: actions/setup-python@v5
with:
  python-version: '3.11'
```
Installs Python 3.11 for running the FBC generator script.

### 3. Install Dependencies
```bash
pip install pyyaml
```
Installs PyYAML library required for YAML processing.

### 4. Download opm CLI
Downloads the `opm` (Operator Package Manager) tool from the official operator-framework repository. This tool is used for:
- Generating the Dockerfile for the catalog
- Validating the FBC format
- Building the catalog image

### 5. Generate FBC YAML
```bash
python scripts/generate-fbc.py
```
Executes the Python script that:
- Scans `catalog/` directory for `operator.yaml` files
- Validates configurations
- Generates FBC format YAML in `catalog/fbc/catalog.yaml`
- Creates package, bundle, and channel entries

### 6. Validate FBC
```bash
opm validate catalog/fbc
```
Uses `opm` to validate the generated FBC structure according to OLM specifications.

### 7. Log in to Container Registry
```yaml
uses: docker/login-action@v3
```
Authenticates with GitHub Container Registry (ghcr.io) using the automatically provided `GITHUB_TOKEN`.

**Permissions Required:**
- `contents: read` - Read repository contents
- `packages: write` - Push to GitHub Packages/Container Registry

### 8. Extract Metadata
Generates image tags:
- **Timestamp**: YYYYMMDDHHmmss format (e.g., `20260126143025`)
- **Short SHA**: First 7 characters of commit SHA (e.g., `abc1234`)

### 9. Build and Push Catalog Image
```bash
# Generate Dockerfile
opm generate dockerfile catalog/fbc

# Build with multiple tags
docker build -f catalog/fbc.Dockerfile \
  -t ghcr.io/org/catalog:latest \
  -t ghcr.io/org/catalog:20260126143025 \
  -t ghcr.io/org/catalog:abc1234 \
  catalog/fbc

# Push all tags
docker push ghcr.io/org/catalog:latest
docker push ghcr.io/org/catalog:20260126143025
docker push ghcr.io/org/catalog:abc1234
```

### 10. Output Image Details
Creates a job summary showing the published image tags.

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `REGISTRY` | `ghcr.io` | Container registry URL |
| `IMAGE_NAME` | `${{ github.repository }}/catalog` | Full image name |

## Image Tags

Each successful build produces three image tags:

1. **`latest`**: Always points to the most recent build
   - Use for: Development and testing
   - Updates: Every successful build

2. **`<timestamp>`**: Build timestamp
   - Format: `YYYYMMDDHHmmss`
   - Use for: Specific point-in-time references
   - Example: `20260126143025`

3. **`<short-sha>`**: Git commit SHA
   - Format: First 7 characters of commit hash
   - Use for: Traceability to source code
   - Example: `abc1234`

## Permissions

The workflow requires the following GitHub token permissions:

```yaml
permissions:
  contents: read      # Read repository files
  packages: write     # Push to GitHub Container Registry
```

These are automatically provided by GitHub Actions when using `GITHUB_TOKEN`.

## Registry Authentication

The workflow uses GitHub's automatic token authentication:

```yaml
username: ${{ github.actor }}          # The user who triggered the workflow
password: ${{ secrets.GITHUB_TOKEN }}  # Automatically provided token
```

## Customization

### Change Registry

To use a different container registry (e.g., Docker Hub, Quay.io):

1. Update the `REGISTRY` environment variable:
   ```yaml
   env:
     REGISTRY: docker.io
     IMAGE_NAME: myorg/catalog
   ```

2. Add registry credentials to repository secrets:
   - Settings → Secrets → Actions
   - Add `DOCKER_USERNAME` and `DOCKER_PASSWORD`

3. Update the login step:
   ```yaml
   - name: Log in to Container Registry
     uses: docker/login-action@v3
     with:
       registry: ${{ env.REGISTRY }}
       username: ${{ secrets.DOCKER_USERNAME }}
       password: ${{ secrets.DOCKER_PASSWORD }}
   ```

### Change Trigger Paths

Add or remove paths in the workflow file:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'catalog/**'
      - '.github/workflows/build-catalog.yml'
      - 'scripts/generate-fbc.py'
      - 'docs/**'  # Add documentation
```

### Add Notifications

Add a notification step at the end:

```yaml
- name: Notify on Slack
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Catalog image published: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Troubleshooting

### Build Failures

1. **Validation Errors**
   - Check GitHub Actions logs
   - Run `make validate` locally
   - Fix issues in `operator.yaml` files

2. **Push Failures**
   - Verify GitHub Packages is enabled
   - Check repository permissions
   - Ensure `GITHUB_TOKEN` has `packages: write`

3. **Python Script Errors**
   - Review operator.yaml syntax
   - Check for missing required fields
   - Ensure logo files exist

### Testing Locally

Before pushing, test the workflow locally:

```bash
# Install dependencies
make install-deps

# Generate FBC
make generate

# Validate
make validate

# Build image (if opm installed)
make build
```

## Security Considerations

1. **Token Scope**: The `GITHUB_TOKEN` is scoped to the repository
2. **Image Visibility**: Images pushed to ghcr.io inherit repository visibility
3. **Pull Secrets**: Public repositories = public images, private repositories = authentication required

## Monitoring

Monitor workflow runs:
- Repository → Actions tab
- Click on workflow run for detailed logs
- Check "Build and Push FBC Catalog" workflow

## Performance

Typical workflow duration:
- Checkout: 5-10 seconds
- Python setup: 10-15 seconds
- FBC generation: 2-5 seconds
- Image build: 30-60 seconds
- Image push: 20-40 seconds

**Total**: ~1-2 minutes per run

## Next Steps

After successful workflow run:

1. Verify images in GitHub Packages:
   - Repository → Packages
   - Check all three tags exist

2. Update CatalogSource:
   ```yaml
   image: ghcr.io/<org>/brtrm-dev-catalog/catalog:latest
   ```

3. Apply to cluster:
   ```bash
   kubectl apply -f catalogsource.yaml
   ```

4. Verify in OLM:
   ```bash
   kubectl get catalogsource -n olm
   kubectl get packagemanifest | grep <operator-name>
   ```
