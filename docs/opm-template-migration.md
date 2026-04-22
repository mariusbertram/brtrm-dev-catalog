# OPM Template Workflow - Migration Complete

## ✅ System auf OPM Templates umgestellt!

Das gesamte System wurde umgestellt, um die **offiziellen OPM Catalog Templates** zu verwenden, anstatt manuell FBC zu generieren.

---

## 🎯 Was ist neu?

### Vorher (Custom Python Generator)
```
operator.yaml (custom format)
  ↓ Python Script
FBC (olm.package, olm.bundle, olm.channel)
  ↓ opm generate dockerfile
Docker Image
```

### Nachher (OPM Basic Template)
```
operator.yaml (olm.template.basic format)
  ↓ combine-templates.py
catalog-template.yaml (combined)
  ↓ opm alpha render-template basic
FBC (olm.package, olm.bundle, olm.channel)
  ↓ opm generate dockerfile  
Docker Image
```

---

## 📝 Neue operator.yaml Struktur

### OPM Basic Template Format

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: my-operator
    defaultChannel: stable
    description: My operator description
    icon:
      base64data: logo/logo.svg  # Wird automatisch encoded
      mediatype: image/svg+xml
      
  - schema: olm.channel
    package: my-operator
    name: stable
    entries:
      - name: my-operator.v1.0.0
      - name: my-operator.v1.1.0
        replaces: my-operator.v1.0.0
        
  - schema: olm.bundle
    image: ghcr.io/org/my-operator-bundle:v1.0.0
    
  - schema: olm.bundle
    image: ghcr.io/org/my-operator-bundle:v1.1.0
```

### Vorteile

1. **Offizieller OLM Standard** - Kein Custom-Format mehr
2. **Weniger Code** - Nur Bundle-Image-Referenzen nötig
3. **OPM macht die Arbeit** - Bundle-Metadaten werden automatisch aus Registry gelesen
4. **Flexibler** - Volle Kontrolle über Upgrade-Graph (replaces, skips, etc.)
5. **Besser dokumentiert** - Offizielle OLM-Dokumentation gilt

---

## 🔄 Workflow-Schritte

### 1. Combine Templates (Python)

```bash
python scripts/combine-templates.py
```

**Was es tut:**
- Scannt `catalog/` nach operator.yaml Dateien
- Lädt jede operator.yaml (im Basic Template Format)
- Encoded Logo-Dateien zu Base64
- Kombiniert alle Entries in eine `catalog-template.yaml`

### 2. Render Template (OPM)

```bash
opm alpha render-template basic catalog/catalog-template.yaml > catalog/fbc/catalog.yaml
```

**Was OPM tut:**
- Lädt Bundle-Images aus der Registry
- Extrahiert Bundle-Metadaten (CSV, CRDs, etc.)
- Generiert vollständiges FBC mit allen Properties
- Fügt relatedImages, GVKs, etc. hinzu

### 3. Generate Dockerfile (OPM)

```bash
opm generate dockerfile catalog/fbc
```

### 4. Build Image (Docker)

```bash
docker build -f catalog/fbc.Dockerfile -t catalog:latest catalog/fbc
```

---

## 📂 Verzeichnisstruktur

```
catalog/
├── ip-rule-operator/
│   ├── operator.yaml           # OPM Basic Template
│   └── logo/logo.svg
│
├── another-operator/
│   └── operator.yaml
│
├── catalog-template.yaml       # Generiert: Combined template
└── fbc/
    └── catalog.yaml            # Generiert: Rendered FBC
```

---

## 🚀 GitHub Actions Workflow

### Neue Steps:

```yaml
- name: Combine operator templates
  run: python scripts/combine-templates.py

- name: Render FBC from template
  run: |
    mkdir -p catalog/fbc
    opm alpha render-template basic catalog/catalog-template.yaml -o yaml > catalog/fbc/catalog.yaml

- name: Validate FBC
  run: opm validate catalog/fbc

- name: Build and push catalog image
  run: |
    opm generate dockerfile catalog/fbc
    docker build -f catalog/fbc.Dockerfile -t ${IMAGE_TAG}:latest catalog/fbc
    docker push ${IMAGE_TAG}:latest
```

---

## 📖 Operator Template Beispiele

### Einfacher Operator (Ein Bundle)

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: simple-operator
    defaultChannel: stable
    description: A simple operator
    
  - schema: olm.channel
    package: simple-operator
    name: stable
    entries:
      - name: simple-operator.v1.0.0
      
  - schema: olm.bundle
    image: ghcr.io/org/simple-operator-bundle:v1.0.0
```

### Operator mit Upgrade-Pfad

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: complex-operator
    defaultChannel: stable
    description: A complex operator with upgrade path
    
  - schema: olm.channel
    package: complex-operator
    name: stable
    entries:
      - name: complex-operator.v1.0.0
      - name: complex-operator.v1.1.0
        replaces: complex-operator.v1.0.0
      - name: complex-operator.v1.2.0
        replaces: complex-operator.v1.1.0
        skips:
          - complex-operator.v1.0.0
          
  - schema: olm.bundle
    image: ghcr.io/org/complex-operator-bundle:v1.0.0
  - schema: olm.bundle
    image: ghcr.io/org/complex-operator-bundle:v1.1.0
  - schema: olm.bundle
    image: ghcr.io/org/complex-operator-bundle:v1.2.0
```

### Multi-Channel Operator

```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: multi-channel-operator
    defaultChannel: stable
    description: Operator with multiple channels
    
  - schema: olm.channel
    package: multi-channel-operator
    name: alpha
    entries:
      - name: multi-channel-operator.v2.0.0-alpha1
      
  - schema: olm.channel
    package: multi-channel-operator
    name: beta
    entries:
      - name: multi-channel-operator.v1.5.0-beta
      
  - schema: olm.channel
    package: multi-channel-operator
    name: stable
    entries:
      - name: multi-channel-operator.v1.4.0
      
  - schema: olm.bundle
    image: ghcr.io/org/multi-channel-operator-bundle:v2.0.0-alpha1
  - schema: olm.bundle
    image: ghcr.io/org/multi-channel-operator-bundle:v1.5.0-beta
  - schema: olm.bundle
    image: ghcr.io/org/multi-channel-operator-bundle:v1.4.0
```

---

## 💡 Upgrade-Graph Keywords

Im Basic Template kannst du folgende Felder in Channel-Entries nutzen:

- **`replaces`** - Direkter Upgrade von einer Version
- **`skips`** - Liste von Versionen, die übersprungen werden können
- **`skipRange`** - Semver Range, die übersprungen werden kann

Beispiel:
```yaml
entries:
  - name: operator.v1.0.0
  - name: operator.v1.1.0
    replaces: operator.v1.0.0
  - name: operator.v1.2.0
    replaces: operator.v1.1.0
    skips:
      - operator.v1.0.0
  - name: operator.v2.0.0
    replaces: operator.v1.2.0
    skipRange: ">=1.0.0 <2.0.0"
```

---

## 🔧 Lokale Entwicklung

### Makefile Commands

```bash
make generate    # Kombiniert Templates und rendert FBC
make validate    # Validiert FBC
make build       # Baut Catalog Image
make serve       # Startet Catalog Server (Port 50051)
make clean       # Löscht generierte Dateien
```

### Manuell testen

```bash
# 1. Templates kombinieren
python3 scripts/combine-templates.py

# 2. Template rendern
opm alpha render-template basic catalog/catalog-template.yaml -o yaml > catalog/fbc/catalog.yaml

# 3. Validieren
opm validate catalog/fbc

# 4. Image bauen
opm generate dockerfile catalog/fbc
docker build -f catalog/fbc.Dockerfile -t test-catalog catalog/fbc

# 5. Image testen
docker run --rm test-catalog ls -la /configs
```

---

## ✅ Vorteile der OPM Templates

### 1. Weniger Code
**Vorher:**
```yaml
bundles:
  - image: ghcr.io/org/bundle:v1.0.0
    version: 1.0.0
    channels: [stable]
    # Mussten Metadaten manuell pflegen
```

**Nachher:**
```yaml
- schema: olm.bundle
  image: ghcr.io/org/bundle:v1.0.0
  # OPM liest Metadaten aus dem Image!
```

### 2. Automatische Metadaten
OPM extrahiert automatisch:
- Package Name und Version
- GVKs (Group/Version/Kind)
- Related Images
- CSV Properties
- Dependencies

### 3. Offizieller Standard
- Dokumentiert in OLM Docs
- Von Operator Framework maintained
- Community Best Practices

### 4. Flexibilität
- Volle Kontrolle über Upgrade-Graph
- Replaces, Skips, SkipRange
- Custom Properties möglich

---

## 📚 Referenzen

- **[OLM Catalog Templates](docs/catalog-templates.md)** - Vollständige Dokumentation
- **[Basic Template Spec](https://olm.operatorframework.io/docs/reference/catalog-templates/#basic-template)**
- **[Semver Template](https://olm.operatorframework.io/docs/reference/catalog-templates/#semver-template)** - Alternative für Semver-basierte Catalogs

---

## 🎓 Semver Template (Optional)

Für Operatoren die Semantic Versioning strict folgen, gibt es auch das **Semver Template**:

```yaml
schema: olm.semver
GenerateMajorChannels: true
GenerateMinorChannels: true
Candidate:
  Bundles:
    - Image: ghcr.io/org/operator:v0.1.0
    - Image: ghcr.io/org/operator:v0.2.0
    - Image: ghcr.io/org/operator:v1.0.0
Fast:
  Bundles:
    - Image: ghcr.io/org/operator:v1.0.0
Stable:
  Bundles:
    - Image: ghcr.io/org/operator:v1.0.0
```

OPM generiert automatisch:
- Channels pro Major/Minor Version
- Upgrade Edges basierend auf Semver
- Skip-Listen für Patch-Versionen

---

## ✅ Migration Checklist

- [x] operator.yaml zu OPM Basic Template Format konvertiert
- [x] combine-templates.py Script erstellt
- [x] GitHub Actions Workflow aktualisiert
- [x] Makefile aktualisiert
- [x] .gitignore aktualisiert
- [x] Lokaler Test erfolgreich
- [x] Dokumentation erstellt

---

## 🎉 Fertig!

Das System nutzt jetzt **offizielle OPM Catalog Templates** und ist:
- ✅ Standard-konform
- ✅ Einfacher zu warten
- ✅ Flexibler
- ✅ Besser dokumentiert

**Nächster Schritt:** Commit und push, dann in GitHub Actions testen!
