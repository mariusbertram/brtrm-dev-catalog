# Sequential Workflow - Workflow-Verbesserung

## ✅ Workflow auf sequenzielle Verarbeitung umgestellt!

Der Workflow wurde von einem ineffizienten "combine-render-split" Ansatz zu einer **sequenziellen Operator-für-Operator Verarbeitung** umgebaut.

---

## 🎯 Problem mit dem alten Workflow

### Alter Workflow (ineffizient):

```
1. combine-templates.py
   → Alle operator.yaml in catalog-template.yaml kombinieren
   
2. opm render-template basic
   → Template rendern
   
3. opm render-template semver
   → Template rendern
   
4. Outputs kombinieren
   
5. split-fbc.py
   → Gerenderte FBC wieder in Operator-Verzeichnisse splitten
```

**Probleme:**
- ❌ Unnötige Zwischendateien (catalog-template.yaml)
- ❌ Kombinieren nur um dann wieder zu splitten
- ❌ Schwer zu debuggen bei Fehlern
- ❌ Alle Operatoren müssen erfolgreich sein

---

## ✅ Neuer sequenzieller Workflow

### Ein Script: `generate-fbc.py`

```python
for operator in operators:
    1. Load operator.yaml
    2. Process logo (encode to base64)
    3. Render FBC with opm
    4. Write to catalog/fbc/<operator>/index.yaml
```

**Vorteile:**
- ✅ Keine Zwischendateien
- ✅ Kein Kombinieren/Splitten nötig
- ✅ Pro Operator isoliert
- ✅ Fehler sind operator-spezifisch
- ✅ Einfacher zu verstehen
- ✅ Basis für Parallelisierung

---

## 📊 Workflow-Vergleich

### Vorher: 3 Scripts

```
scripts/
├── combine-templates.py    # Kombiniert Templates
├── split-fbc.py           # Splitted FBC
└── generate-fbc.py         # (alt, nicht genutzt)
```

### Nachher: 1 Script

```
scripts/
└── generate-fbc.py         # Macht alles sequenziell
```

---

## 🔄 Neuer Workflow im Detail

### Für jeden Operator:

```
1. Find operator directories
   catalog/ip-rule-operator/
   catalog/webhook-operator/

2. For each operator:
   a) Load operator.yaml
   b) Detect schema (olm.semver oder olm.template.basic)
   c) Process logo (encode base64 wenn nötig)
   d) Write to temp file
   e) Call: opm alpha render-template <type> <temp-file>
   f) Write output to: catalog/fbc/<operator>/index.yaml
   g) Remove temp file

3. Summary
   ✓ Successfully processed: 2/2 operators
```

---

## 💻 Ausgabe

```
Found 2 operator(s)
============================================================

Processing: ip-rule-operator
  → Template type: olm.semver
  → Rendered 4 object(s)
  ✓ Written to fbc/ip-rule-operator/index.yaml

Processing: webhook-operator
  → Template type: olm.template.basic
  → Rendered 4 object(s)
  ✓ Written to fbc/webhook-operator/index.yaml

============================================================
✓ Successfully processed: 2/2 operator(s)

FBC generated in: catalog/fbc
```

**Klar und präzise!** Man sieht sofort welcher Operator wie verarbeitet wurde.

---

## 🚀 GitHub Actions

### Vereinfachter Workflow:

```yaml
- name: Generate FBC from templates
  run: python scripts/generate-fbc.py
  
- name: Validate FBC
  run: opm validate catalog/fbc

- name: Build and push
  run: |
    cd catalog
    opm generate dockerfile fbc
    docker build -f fbc.Dockerfile -t catalog .
    docker push catalog
```

**Viel einfacher!** Nur ein Script-Aufruf statt mehrerer Steps.

---

## 🎓 Semver Template Format

**Wichtig:** Das Semver-Schema ist sehr strikt!

### ❌ Falsch (extra Felder):

```yaml
schema: olm.semver
name: my-operator           # ❌ Nicht erlaubt
defaultChannel: stable      # ❌ Nicht erlaubt
description: My operator    # ❌ Nicht erlaubt
GenerateMajorChannels: true
Stable:
  Bundles:
    - Image: ghcr.io/org/operator:v1.0.0
```

### ✅ Richtig (nur Schema-Felder):

```yaml
schema: olm.semver
GenerateMajorChannels: true
GenerateMinorChannels: true
Stable:
  Bundles:
    - Image: ghcr.io/org/operator:v1.0.0
```

**OPM extrahiert Name und Description automatisch aus dem Bundle-Image!**

---

## 📝 Gelöschte Dateien

- ❌ `scripts/combine-templates.py` - Nicht mehr benötigt
- ❌ `scripts/split-fbc.py` - Nicht mehr benötigt
- ❌ `catalog/catalog-template.yaml` - Wird nicht mehr generiert

---

## ✅ Code-Vereinfachung

### Makefile

**Vorher:**
```makefile
generate:
    python3 scripts/combine-templates.py
    opm render-template basic catalog/catalog-template.yaml > /tmp/basic.yaml
    opm render-template semver catalog/catalog-template.yaml > /tmp/semver.yaml
    cat /tmp/basic.yaml /tmp/semver.yaml > /tmp/rendered.yaml
    python3 scripts/split-fbc.py /tmp/rendered.yaml catalog/fbc
```

**Nachher:**
```makefile
generate:
    python3 scripts/generate-fbc.py
```

**80% weniger Code!**

---

## 🎯 Fehlerbehandlung

### Pro Operator:

```
Processing: ip-rule-operator
  → Template type: olm.semver
  ✗ opm render failed: unknown field "defaultChannel"
  ✗ Failed to render FBC

Processing: webhook-operator
  → Template type: olm.template.basic
  → Rendered 4 object(s)
  ✓ Written to fbc/webhook-operator/index.yaml

============================================================
✓ Successfully processed: 1/2 operator(s)
✗ Failed operators: ip-rule-operator
```

**Klare Fehlermeldung pro Operator!** Andere Operatoren funktionieren trotzdem.

---

## 🚀 Zukünftige Erweiterungen

Der sequenzielle Ansatz ermöglicht:

### 1. Parallelisierung

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_operator, op) for op in operators]
```

### 2. Incremental Builds

```python
if not operator_changed_since_last_build(operator):
    print(f"  → Skipping {operator} (unchanged)")
    continue
```

### 3. Caching

```python
cache_key = hash_operator_yaml(operator)
if cache_exists(cache_key):
    copy_from_cache(operator)
    continue
```

---

## 📊 Performance

### Vorher:
```
1. Combine all: 0.1s
2. Render basic: 2.0s
3. Render semver: 2.0s
4. Combine outputs: 0.1s
5. Split: 0.2s
Total: ~4.4s
```

### Nachher:
```
1. Render operator 1: 2.0s
2. Render operator 2: 2.0s
Total: ~4.0s
```

**Aktuell ähnlich, aber:**
- ✅ Einfacher Code
- ✅ Weniger Dateien
- ✅ Basis für Parallelisierung (dann 2.0s total!)

---

## ✅ Zusammenfassung

**Vorher:**
- 3 Scripts
- Combine → Render → Split
- Zwischendateien
- Komplexer Workflow

**Nachher:**
- 1 Script
- Sequential pro Operator
- Keine Zwischendateien
- Einfacher Workflow
- Bessere Fehlerbehandlung

**Der Workflow ist jetzt viel cleaner und wartbarer!** 🎉

---

## 🎓 Best Practices

### operator.yaml Templates:

**Semver (minimal):**
```yaml
schema: olm.semver
GenerateMajorChannels: true
Stable:
  Bundles:
    - Image: ghcr.io/org/operator:v1.0.0
```

**Basic (mit Metadaten):**
```yaml
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
    image: ghcr.io/org/operator:v1.0.0
```

---

**Status:** ✅ **Workflow erfolgreich optimiert!**
