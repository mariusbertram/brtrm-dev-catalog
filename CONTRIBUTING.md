# Contributing Guide

## Neuen Operator hinzufügen

### Option 1: Semver Template (Empfohlen für mehrere Versionen)

#### 1. Verzeichnis erstellen

```bash
mkdir -p catalog/<operator-name>
```

#### 2. operator.yaml erstellen (Semver)

```yaml
schema: olm.semver
name: <operator-name>
defaultChannel: stable
description: <Beschreibung>
icon:                           # Optional
  base64data: logo/logo.svg
  mediatype: image/svg+xml

GenerateMajorChannels: true
GenerateMinorChannels: true

Stable:
  Bundles:
    - Image: <registry>/<org>/<operator-name>-bundle:v1.0.0
    - Image: <registry>/<org>/<operator-name>-bundle:v1.1.0

Candidate:
  Bundles:
    - Image: <registry>/<org>/<operator-name>-bundle:v2.0.0-rc1
```

**Vorteile:**
- Automatische Channel-Generierung (stable, stable-v1, stable-v1.0, etc.)
- Automatische Upgrade-Pfade basierend auf Semver
- Ideal für viele Versionen

### Option 2: Basic Template (für einfache Operatoren)

#### 1. Verzeichnis erstellen

```bash
mkdir -p catalog/<operator-name>
```

#### 2. operator.yaml erstellen (Basic)

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: <operator-name>
    defaultChannel: stable
    description: <Beschreibung>
    icon:                           # Optional
      base64data: logo/logo.svg
      mediatype: image/svg+xml
  
  - schema: olm.channel
    package: <operator-name>
    name: stable
    entries:
      - name: <operator-name>.v1.0.0
  
  - schema: olm.bundle
    image: <registry>/<org>/<operator-name>-bundle:v1.0.0
```

**Vorteile:**
- Volle Kontrolle über Channels
- Manuelle Upgrade-Pfad-Definition
- Einfacher für Single-Version-Operatoren

### 3. Optional: Logo hinzufügen

```bash
mkdir -p catalog/<operator-name>/logo
cp logo.svg catalog/<operator-name>/logo/
```

### 4. Lokal testen

```bash
make generate
make validate
```

### 5. Pull Request erstellen

```bash
git add catalog/<operator-name>
git commit -m "Add <operator-name> to catalog"
git push
```

## Mehrere Versionen verwalten (Semver Template)

Das Semver Template macht es einfach, mehrere Versionen zu verwalten:

```yaml
schema: olm.semver
name: my-operator
defaultChannel: stable
description: My operator

GenerateMajorChannels: true     # Erstellt stable-v1, stable-v2, etc.
GenerateMinorChannels: false    # Keine stable-v1.0, stable-v1.1

Stable:
  Bundles:
    - Image: ghcr.io/org/my-operator:v1.0.0
    - Image: ghcr.io/org/my-operator:v1.1.0
    - Image: ghcr.io/org/my-operator:v1.2.0
    - Image: ghcr.io/org/my-operator:v2.0.0

Candidate:
  Bundles:
    - Image: ghcr.io/org/my-operator:v2.1.0-rc1

Fast:
  Bundles:
    - Image: ghcr.io/org/my-operator:v2.1.0
```

**OPM generiert automatisch:**
- `stable` - Neueste stabile Version (v2.0.0)
- `stable-v1` - Neueste v1.x Version (v1.2.0)
- `stable-v2` - Neueste v2.x Version (v2.0.0)
- `candidate` - Release Candidates
- `fast` - Early Access Versionen

## Upgrade-Pfad definieren (Basic Template)

Für manuelle Kontrolle über Upgrades:

```yaml
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
```

## Multi-Channel Operator

```yaml
entries:
  - schema: olm.package
    name: my-operator
    defaultChannel: stable
    description: My operator
  
  - schema: olm.channel
    package: my-operator
    name: alpha
    entries:
      - name: my-operator.v2.0.0-alpha
  
  - schema: olm.channel
    package: my-operator
    name: stable
    entries:
      - name: my-operator.v1.0.0
  
  - schema: olm.bundle
    image: ghcr.io/org/my-operator:v2.0.0-alpha
  - schema: olm.bundle
    image: ghcr.io/org/my-operator:v1.0.0
```

## Requirements

- Bundle-Image muss öffentlich zugänglich sein (oder Registry-Auth konfiguriert)
- Bundle muss valides OLM-Bundle-Format haben
- Operator-Name muss eindeutig sein
