# IP Rules Catalog

File-Based Catalog (FBC) für Kubernetes Operators mit **OPM Catalog Templates** (Basic und Semver).

## 🚀 Quick Start

### Neuen Operator hinzufügen (Semver Template - Empfohlen für mehrere Versionen)

```bash
# 1. Verzeichnis erstellen
mkdir -p catalog/my-operator

# 2. operator.yaml erstellen (OPM Semver Template Format)
cat > catalog/my-operator/operator.yaml <<'EOF'
schema: olm.semver
name: my-operator
defaultChannel: stable
description: My operator description

# Automatische Channel-Generierung
GenerateMajorChannels: true
GenerateMinorChannels: true

# Bundles für verschiedene Channels
Stable:
  Bundles:
    - Image: ghcr.io/org/my-operator-bundle:v1.0.0
    - Image: ghcr.io/org/my-operator-bundle:v1.1.0
    - Image: ghcr.io/org/my-operator-bundle:v2.0.0

Candidate:
  Bundles:
    - Image: ghcr.io/org/my-operator-bundle:v2.1.0-rc1

Fast:
  Bundles:
    - Image: ghcr.io/org/my-operator-bundle:v2.1.0
EOF

# 3. Commit und push
git add catalog/my-operator
git commit -m "Add my-operator"
git push
```

### Alternative: Basic Template (für einfache Operatoren)

```bash
cat > catalog/my-operator/operator.yaml <<'EOF'
schema: olm.template.basic
entries:
  - schema: olm.package
    name: my-operator
    defaultChannel: stable
    description: My operator description
    
  - schema: olm.channel
    package: my-operator
    name: stable
    entries:
      - name: my-operator.v1.0.0
      
  - schema: olm.bundle
    image: ghcr.io/org/my-operator-bundle:v1.0.0
EOF
```

Der GitHub Actions Workflow baut automatisch ein neues Catalog-Image!

## 📁 Struktur

### Source (Git-committed)
```
catalog/
├── ip-rule-operator/
│   ├── operator.yaml      # OPM Basic Template
│   └── logo/logo.svg      # Optional
└── webhook-operator/
    └── operator.yaml
```

### Generated (git-ignored)
```
catalog/
├── catalog-template.yaml  # Combined templates
├── fbc.Dockerfile         # Generated Dockerfile
└── fbc/                   # Rendered FBC
    ├── ip-rule-operator/
    │   └── index.yaml
    └── webhook-operator/
        └── index.yaml
```

## 📝 operator.yaml Formate

### Semver Template (Empfohlen für mehrere Versionen)

Das **Semver Template** ist ideal für Operatoren mit mehreren Versionen. OPM generiert automatisch Channels und Upgrade-Pfade basierend auf Semantic Versioning.

```yaml
schema: olm.semver
name: operator-name
defaultChannel: stable
description: Operator description
icon:                              # Optional
  base64data: logo/logo.svg        # Wird automatisch encoded
  mediatype: image/svg+xml

# Channel-Generierung
GenerateMajorChannels: true        # Erstellt Channel pro Major-Version (v1, v2)
GenerateMinorChannels: true        # Erstellt Channel pro Minor-Version (v1.0, v1.1)

# Bundle-Definitionen nach Channel
Stable:                            # Produktions-Channel
  Bundles:
    - Image: ghcr.io/org/operator:v1.0.0
    - Image: ghcr.io/org/operator:v1.1.0
    - Image: ghcr.io/org/operator:v2.0.0

Candidate:                         # Release-Candidate Channel
  Bundles:
    - Image: ghcr.io/org/operator:v2.1.0-rc1

Fast:                              # Early-Access Channel
  Bundles:
    - Image: ghcr.io/org/operator:v2.1.0
```

**OPM generiert automatisch:**
- Channels: `stable`, `candidate`, `fast`, `stable-v1`, `stable-v2`, `stable-v1.0`, `stable-v1.1`, etc.
- Upgrade-Edges basierend auf Semver-Regeln
- Skip-Listen für Patch-Versionen

### Basic Template (für einfache Operatoren)

Das **Basic Template** gibt volle Kontrolle über Channels und Upgrade-Pfade.

```yaml
schema: olm.template.basic
entries:
  # Package Definition
  - schema: olm.package
    name: operator-name
    defaultChannel: stable
    description: Operator description
    icon:                           # Optional
      base64data: logo/logo.svg     # Wird automatisch encoded
      mediatype: image/svg+xml
  
  # Channel Definitionen
  - schema: olm.channel
    package: operator-name
    name: stable
    entries:
      - name: operator-name.v1.0.0
      - name: operator-name.v1.1.0
        replaces: operator-name.v1.0.0
      - name: operator-name.v2.0.0
        replaces: operator-name.v1.1.0
        skipRange: ">=1.0.0 <2.0.0"
  
  # Bundle Referenzen
  - schema: olm.bundle
    image: ghcr.io/org/operator-bundle:v1.0.0
  - schema: olm.bundle
    image: ghcr.io/org/operator-bundle:v1.1.0
  - schema: olm.bundle
    image: ghcr.io/org/operator-bundle:v2.0.0
```

**Wichtig:** OPM extrahiert automatisch alle Metadaten (CSV, CRDs, etc.) aus den Bundle-Images!

## 🔄 Workflow

```
Für jeden Operator sequenziell:
  operator.yaml (basic oder semver)
    ↓
  opm alpha render-template
    ↓
  catalog/fbc/<operator>/index.yaml

Dann:
  catalog/fbc/ (alle Operatoren)
    ↓
  opm validate
    ↓
  docker build
    ↓
  Catalog Image
```

**Vorteile des sequenziellen Ansatzes:**
- ✅ Einfacher Workflow - keine Zwischendateien
- ✅ Pro Operator isoliert verarbeitet
- ✅ Fehler pro Operator identifizierbar
- ✅ Parallele Verarbeitung möglich (zukünftig)

**Unterstützte Template-Typen:**
- `olm.template.basic` - Manuelle Channel/Bundle-Definitionen
- `olm.semver` - Automatische Channel-Generierung basierend auf Semver

## 💻 Lokale Entwicklung

```bash
# Generiere FBC
make generate

# Validiere
make validate

# Baue Image lokal
make build

# Starte Catalog Server
make serve

# Aufräumen
make clean

# Hilfe
make help
```

## 🐳 Catalog Images

GitHub Actions published nach:
- `ghcr.io/<org>/brtrm-dev-catalog/catalog:latest`
- `ghcr.io/<org>/brtrm-dev-catalog/catalog:<timestamp>`
- `ghcr.io/<org>/brtrm-dev-catalog/catalog:<commit-sha>`

## 🚢 Deployment

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: brtrm-dev-catalog
  namespace: olm
spec:
  sourceType: grpc
  image: ghcr.io/<org>/brtrm-dev-catalog/catalog:latest
  displayName: IP Rules Catalog
  publisher: Your Organization
  updateStrategy:
    registryPoll:
      interval: 10m
```

```bash
kubectl apply -f catalogsource.yaml
kubectl get packagemanifest | grep -E "ip-rule|webhook"
```

## 📖 Weitere Informationen

- **[OPM Template Migration](docs/opm-template-migration.md)** - Details zum OPM Template Workflow
- **[FBC Split Directories](docs/fbc-split-directories.md)** - Warum Operatoren in separate Verzeichnisse gesplittet werden
- **[Final Working Workflow](docs/final-working-workflow.md)** - Kompletter Workflow-Überblick
- **[File-Based Catalogs](docs/file-based-catalogs.md)** - OLM FBC Spezifikation
- **[Catalog Templates](docs/catalog-templates.md)** - OLM Template Dokumentation
- **[GitHub Actions](docs/github-actions.md)** - Workflow-Details

## ⚙️ Technische Details

- **Python 3.11+** - Template-Kombination und FBC-Splitting
- **OPM v1.48.0+** - Template-Rendering und Validation
- **Docker** - Image-Building
- **GitHub Actions** - CI/CD
- **GitHub Container Registry** - Image-Storage

## 🤝 Contributing

1. Erstelle einen neuen Operator in `catalog/<operator-name>/`
2. Folge dem OPM Basic Template Format
3. Teste lokal mit `make generate && make validate`
4. Erstelle Pull Request

## 📄 License

[Deine Lizenz]

### Required Fields

The following fields are **required** in `operator.yaml`:
- `name`: The package name for the operator
- `description`: A description of what the operator does
- `defaultChannel`: The default channel (must exist in channels list)
- `channels`: List of channel objects with `name` field
- `bundles`: List of bundle objects, each containing:
  - `image`: The bundle image reference
  - `version`: The semantic version
  - `channels`: List of channels this bundle is part of

### Optional Fields

- `logo`: Relative path to the operator logo (SVG, PNG, or JPEG)

### Validation

The build process will validate that:
- All required fields are present
- The default channel exists in the channels list
- Each bundle has an image, version, and channel assignment
- All bundle channel references exist in the channels list

## Automatic Build Process

The catalog is automatically built and published when changes are pushed to the `catalog/` directory.

### GitHub Actions Workflow

The workflow (`.github/workflows/build-catalog.yml`) performs the following steps:

1. **Checkout**: Clones the repository
2. **Generate FBC**: Runs `scripts/generate-fbc.py` to create FBC YAML from operator configs
3. **Validate**: Uses `opm validate` to check the FBC format
4. **Build**: Creates a catalog container image using `opm`
5. **Push**: Publishes the image to GitHub Container Registry (ghcr.io)

### Image Tags

The catalog image is published with multiple tags:
- `latest`: Always points to the most recent build
- `<timestamp>`: Build timestamp (YYYYMMDDHHmmss)
- `<short-sha>`: First 7 characters of the git commit SHA

### Manual Build

To build the catalog locally:

```bash
# Install dependencies
pip install pyyaml

# Generate FBC
python scripts/generate-fbc.py

# Validate FBC
opm validate catalog/fbc

# Build and serve locally
opm serve catalog/fbc -p 50051
```

## Adding a New Operator

1. Create a new directory under `catalog/`:
   ```bash
   mkdir -p catalog/my-operator/logo
   ```

2. Add your operator logo (optional):
   ```bash
   cp my-logo.svg catalog/my-operator/logo/logo.svg
   ```

3. Create `catalog/my-operator/operator.yaml`:
   ```yaml
   name: my-operator
   logo: logo/logo.svg
   defaultChannel: stable
   description: My awesome operator
   
   channels:
     - name: stable
   
   bundles:
     - image: ghcr.io/myorg/my-operator-bundle:v0.1.0
       version: 0.1.0
       channels:
         - stable
   ```

4. Commit and push:
   ```bash
   git add catalog/my-operator
   git commit -m "Add my-operator to catalog"
   git push
   ```

5. The GitHub Actions workflow will automatically build and publish the updated catalog.

## Using the Catalog

To use this catalog in your Kubernetes cluster:

1. Create a CatalogSource:
   ```yaml
   apiVersion: operators.coreos.com/v1alpha1
   kind: CatalogSource
   metadata:
     name: brtrm-dev-catalog
     namespace: olm
   spec:
     sourceType: grpc
     image: ghcr.io/<your-org>/brtrm-dev-catalog/catalog:latest
     displayName: IP Rules Catalog
     updateStrategy:
       registryPoll:
         interval: 10m
   ```

2. Apply the CatalogSource:
   ```bash
   kubectl apply -f catalogsource.yaml
   ```

3. The operators will now be available in the OperatorHub.

## Troubleshooting

### Build Failures

Check the GitHub Actions logs for details. Common issues:
- Missing required fields in `operator.yaml`
- Invalid YAML syntax
- Bundle image references don't exist
- Channel names mismatch between channels and bundle assignments

### Local Validation

Run the generator locally to check for errors:
```bash
python scripts/generate-fbc.py
```

This will validate all operator configurations and report any errors.

## References

- [File-Based Catalogs Documentation](docs/file-based-catalogs.md)
- [Catalog Templates](docs/catalog-templates.md)
- [OLM Documentation](https://olm.operatorframework.io/)
- [Operator Registry](https://github.com/operator-framework/operator-registry)
