# ✅ Finaler funktionierender Workflow

## 🎉 Status: Produktionsbereit!

Der Workflow wurde erfolgreich auf **OPM Templates** umgestellt und funktioniert korrekt.

---

## 🔧 Die finale Lösung

### Docker Build Context

**Schlüssel zum Erfolg:**
```yaml
- name: Build and push catalog image
  run: |
    cd catalog                              # ← Wechsel ins catalog/ Verzeichnis
    opm generate dockerfile fbc             # Generiert catalog/fbc.Dockerfile
    docker build -f fbc.Dockerfile ... .    # Build-Kontext ist . (= catalog/)
```

**Warum das funktioniert:**

```
catalog/                    ← Working Directory & Build Context
├── fbc/                    ← Wird kopiert
│   └── catalog.yaml
└── fbc.Dockerfile         ← Dockerfile
```

Das Dockerfile enthält:
```dockerfile
ADD fbc /configs
```

Da der Build-Kontext `catalog/` ist, findet Docker `fbc/` → ✅ Funktioniert!

---

## 📊 Kompletter Workflow

### 1. Combine Templates (Python)
```bash
python scripts/combine-templates.py
```
**Output:** `catalog/catalog-template.yaml`

### 2. Render FBC (OPM)
```bash
opm alpha render-template basic catalog/catalog-template.yaml > catalog/fbc/catalog.yaml
```
**Output:** `catalog/fbc/catalog.yaml`

### 3. Generate Dockerfile (OPM)
```bash
cd catalog
opm generate dockerfile fbc
```
**Output:** `catalog/fbc.Dockerfile`

### 4. Build Image (Docker)
```bash
cd catalog
docker build -f fbc.Dockerfile -t catalog:latest .
```
**Build-Kontext:** `catalog/` (aktuelles Verzeichnis)

### 5. Push Image
```bash
docker push catalog:latest
docker push catalog:timestamp
docker push catalog:sha
```

---

## 📁 Verzeichnisstruktur

```
brtrm-dev-catalog/
├── .github/
│   └── workflows/
│       └── build-catalog.yml       # GitHub Actions Workflow
│
├── catalog/
│   ├── ip-rule-operator/
│   │   ├── operator.yaml          # OPM Basic Template
│   │   └── logo/logo.svg
│   │
│   ├── catalog-template.yaml      # Generated: Combined templates
│   ├── fbc.Dockerfile             # Generated: Dockerfile
│   └── fbc/
│       └── catalog.yaml           # Generated: Rendered FBC
│
├── scripts/
│   └── combine-templates.py       # Kombiniert operator.yaml Templates
│
├── docs/
│   └── opm-template-migration.md  # Dokumentation
│
└── Makefile                        # Lokale Commands
```

---

## 🚀 GitHub Actions Workflow

### Vollständiger Ablauf:

```yaml
steps:
  # 1. Setup
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
  
  # 2. Install Tools
  - run: pip install pyyaml
  - run: curl -L .../opm -o /usr/local/bin/opm
  
  # 3. Combine Templates
  - run: python scripts/combine-templates.py
  
  # 4. Render FBC
  - run: |
      mkdir -p catalog/fbc
      opm alpha render-template basic catalog/catalog-template.yaml > catalog/fbc/catalog.yaml
  
  # 5. Validate
  - run: opm validate catalog/fbc
  
  # 6. Build & Push
  - run: |
      cd catalog
      opm generate dockerfile fbc
      docker build -f fbc.Dockerfile -t ${IMAGE} .
      docker push ${IMAGE}:latest
      docker push ${IMAGE}:timestamp
      docker push ${IMAGE}:sha
```

---

## 💻 Lokale Entwicklung

### Makefile Commands

```bash
make generate    # Kombiniert Templates (und rendert wenn opm verfügbar)
make validate    # Validiert FBC (benötigt opm)
make build       # Baut Catalog Image (benötigt opm & docker)
make serve       # Startet Catalog Server (benötigt opm)
make clean       # Löscht generierte Dateien
```

### Manuell testen

```bash
# 1. Templates kombinieren (funktioniert immer)
python3 scripts/combine-templates.py

# 2. FBC rendern (benötigt opm v1.48.0+)
mkdir -p catalog/fbc
opm alpha render-template basic catalog/catalog-template.yaml -o yaml > catalog/fbc/catalog.yaml

# 3. Validieren
opm validate catalog/fbc

# 4. Image bauen
cd catalog
opm generate dockerfile fbc
docker build -f fbc.Dockerfile -t test-catalog .

# 5. Image testen
docker run --rm test-catalog ls -la /configs
docker run --rm test-catalog cat /configs/catalog.yaml | head -50
```

---

## ✅ Wichtige Details

### 1. Working Directory

```yaml
cd catalog    # Wichtig! Alle folgenden Befehle relativ zu catalog/
```

**Warum:**
- `opm generate dockerfile fbc` erstellt `fbc.Dockerfile` im aktuellen Verzeichnis
- Docker Build-Kontext ist `.` (= catalog/)
- Dockerfile `ADD fbc` funktioniert, weil `fbc/` relativ zu catalog/ ist

### 2. Build Context

```bash
docker build -f fbc.Dockerfile ... .
#                                  ^ Build-Kontext ist . (catalog/)
```

**Nicht:**
```bash
docker build -f catalog/fbc.Dockerfile ... catalog/fbc
#                                          ^^^^^^^^^^^^ FALSCH!
```

### 3. OPM Version

GitHub Actions nutzt: **OPM v1.48.0**
- Unterstützt `opm alpha render-template basic`
- Unterstützt `opm generate dockerfile`
- Unterstützt `opm validate`

Lokale Installation kann älter sein:
- `opm alpha render-template` evtl. nicht verfügbar
- Makefile zeigt Warnung statt Fehler

---

## 🎯 Workflow-Trigger

Der Workflow startet bei:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'catalog/**'                          # Operator-Änderungen
      - '.github/workflows/build-catalog.yml' # Workflow-Änderungen
      - 'scripts/combine-templates.py'       # Script-Änderungen
  workflow_dispatch:                          # Manueller Trigger
```

---

## 📦 Generated Artifacts

### Lokal (git-ignored):
- `catalog/catalog-template.yaml` - Combined OPM templates
- `catalog/fbc/catalog.yaml` - Rendered FBC
- `catalog/fbc.Dockerfile` - Generated Dockerfile

### GitHub Container Registry:
- `ghcr.io/<org>/<repo>/catalog:latest`
- `ghcr.io/<org>/<repo>/catalog:<timestamp>`
- `ghcr.io/<org>/<repo>/catalog:<commit-sha>`

---

## 🔍 Debugging

### Pipeline-Logs zeigen:

```
=== Combining operator templates ===
Found 1 operator(s):
  - ip-rule-operator
✓ Combined template written to: catalog/catalog-template.yaml

=== Rendering FBC from Basic Template ===
Total YAML documents: 4
Entry types:
      1 schema: olm.package
      1 schema: olm.bundle
      2 schema: olm.channel
Packages:
  - ip-rule-operator

=== Validating FBC ===
FBC file size: 350 lines
✓ Validation passed

=== Building Docker Image ===
Step 1/4 : FROM quay.io/operator-framework/opm:latest
Step 2/4 : ADD fbc /configs
Step 3/4 : RUN ["/bin/opm", "serve", "/configs", "--cache-dir=/tmp/cache", "--cache-only"]
Step 4/4 : LABEL operators.operatorframework.io.index.configs.v1=/configs
Successfully tagged ghcr.io/.../catalog:latest

=== Pushing Images ===
✓ Pushed ghcr.io/.../catalog:latest
✓ Pushed ghcr.io/.../catalog:20260126143025
✓ Pushed ghcr.io/.../catalog:abc1234
```

---

## 🎓 operator.yaml Beispiele

### Minimales Beispiel

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: my-operator
    defaultChannel: stable
    description: My operator
    
  - schema: olm.channel
    package: my-operator
    name: stable
    entries:
      - name: my-operator.v1.0.0
      
  - schema: olm.bundle
    image: ghcr.io/org/my-operator-bundle:v1.0.0
```

### Mit Logo

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: my-operator
    defaultChannel: stable
    description: My operator
    icon:
      base64data: logo/logo.svg  # Wird auto-encoded
      mediatype: image/svg+xml
  # ...rest wie oben
```

### Mit Upgrade-Pfad

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: my-operator
    defaultChannel: stable
    description: My operator
    
  - schema: olm.channel
    package: my-operator
    name: stable
    entries:
      - name: my-operator.v1.0.0
      - name: my-operator.v1.1.0
        replaces: my-operator.v1.0.0
      - name: my-operator.v2.0.0
        replaces: my-operator.v1.1.0
        skipRange: ">=1.0.0 <2.0.0"
      
  - schema: olm.bundle
    image: ghcr.io/org/my-operator:v1.0.0
  - schema: olm.bundle
    image: ghcr.io/org/my-operator:v1.1.0
  - schema: olm.bundle
    image: ghcr.io/org/my-operator:v2.0.0
```

---

## ✅ Zusammenfassung

### Was funktioniert:

1. ✅ **OPM Templates** - Offizieller Standard
2. ✅ **Combine Script** - Kombiniert alle Operatoren
3. ✅ **Template Rendering** - OPM generiert FBC automatisch
4. ✅ **Docker Build** - Korrekter Kontext (`catalog/`)
5. ✅ **Multi-Tag Push** - latest, timestamp, commit-sha
6. ✅ **Validation** - OPM validate check
7. ✅ **Debug Output** - Umfangreiche Logs

### Key Learnings:

- **`cd catalog`** vor Docker-Befehlen ist essentiell
- **Build-Kontext** muss `.` (catalog/) sein, nicht `fbc/`
- **OPM v1.48.0+** für `render-template` benötigt
- **Logo-Encoding** passiert automatisch im combine-script

---

## 🚀 Ready for Production!

Der Workflow ist:
- ✅ Getestet und funktioniert
- ✅ OLM-Standard-konform
- ✅ Gut dokumentiert
- ✅ Debug-freundlich
- ✅ Multi-Operator-fähig

**Einfach commit & push - der Rest läuft automatisch!** 🎉

---

**Erstellt:** 26. Januar 2026  
**Status:** ✅ Produktionsbereit  
**Workflow-Version:** OPM Templates mit korrektem Build-Kontext
