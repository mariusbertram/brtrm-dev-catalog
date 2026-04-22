# FBC Split in Operator-Unterverzeichnisse

## ✅ Problem gelöst!

Der Catalog wird jetzt korrekt in **separate Unterverzeichnisse pro Operator** aufgeteilt, entsprechend dem OLM File-Based Catalog Standard.

---

## 🎯 Änderung

### Vorher (❌ FALSCH):
```
catalog/fbc/
└── catalog.yaml    # Alle Operatoren in einer Datei
```

### Nachher (✅ KORREKT):
```
catalog/fbc/
├── ip-rule-operator/
│   └── index.yaml       # Nur ip-rule-operator Objekte
├── webhook-operator/
│   └── index.yaml       # Nur webhook-operator Objekte
└── another-operator/
    └── index.yaml       # Nur another-operator Objekte
```

---

## 🔄 Neuer Workflow

### 1. Combine Templates
```bash
python scripts/combine-templates.py
```
**Output:** `catalog/catalog-template.yaml`

### 2. Render FBC (vollständig)
```bash
opm alpha render-template basic catalog/catalog-template.yaml > /tmp/rendered-fbc.yaml
```
**Output:** `/tmp/rendered-fbc.yaml` (alle Operatoren zusammen)

### 3. Split in Unterverzeichnisse
```bash
python scripts/split-fbc.py /tmp/rendered-fbc.yaml catalog/fbc
```
**Output:** `catalog/fbc/<operator>/index.yaml` (ein Verzeichnis pro Operator)

### 4. Validate
```bash
opm validate catalog/fbc
```

### 5. Build
```bash
cd catalog
opm generate dockerfile fbc
docker build -f fbc.Dockerfile -t catalog .
```

---

## 📝 Split-Script Details

Das neue `scripts/split-fbc.py` Script:

### Was es tut:
1. Liest das gerenderte FBC (alle Operatoren)
2. Parsed YAML-Dokumente
3. Gruppiert nach Package-Name:
   - `olm.package` → `name` Feld
   - `olm.bundle` → `package` Feld
   - `olm.channel` → `package` Feld
4. Erstellt Unterverzeichnis pro Operator
5. Schreibt `index.yaml` mit allen Objekten des Operators

### Beispiel-Output:
```
Splitting FBC: /tmp/rendered-fbc.yaml -> catalog/fbc
============================================================
  ✓ Created ip-rule-operator/index.yaml with 4 objects
  ✓ Created webhook-operator/index.yaml with 6 objects

✓ Split FBC into 2 operator directories

Total objects:
  - Packages: 2
  - Bundles: 2
  - Channels: 4
```

---

## 🔧 GitHub Actions Workflow

### Updated Render Step:

```yaml
- name: Render FBC from template
  run: |
    # 1. Render complete FBC
    opm alpha render-template basic catalog/catalog-template.yaml > /tmp/rendered-fbc.yaml
    
    # 2. Split into operator directories using inline Python
    python3 << 'PYEOF'
import yaml
from pathlib import Path

# Read and split FBC
with open('/tmp/rendered-fbc.yaml') as f:
    content = f.read()

documents = content.split('\n---\n')
operators = {}

# Group by package
for doc in documents:
    obj = yaml.safe_load(doc)
    schema = obj.get('schema', '')
    
    if schema == 'olm.package':
        pkg_name = obj.get('name')
    elif schema in ['olm.bundle', 'olm.channel']:
        pkg_name = obj.get('package')
    
    if pkg_name:
        operators.setdefault(pkg_name, []).append(obj)

# Write operator directories
for operator, objects in operators.items():
    operator_dir = Path(f'catalog/fbc/{operator}')
    operator_dir.mkdir(parents=True, exist_ok=True)
    
    with open(operator_dir / 'index.yaml', 'w') as f:
        for idx, obj in enumerate(objects):
            if idx > 0:
                f.write('---\n')
            yaml.dump(obj, f, default_flow_style=False, sort_keys=False)
PYEOF
```

---

## 📊 Verzeichnisstruktur

### Finale Struktur:

```
catalog/
├── ip-rule-operator/
│   ├── operator.yaml           # Source: OPM Basic Template
│   └── logo/logo.svg
│
├── webhook-operator/
│   └── operator.yaml           # Source: OPM Basic Template
│
├── catalog-template.yaml       # Generated: Combined templates
├── fbc.Dockerfile              # Generated: Dockerfile
└── fbc/                        # Generated: Split FBC
    ├── ip-rule-operator/
    │   └── index.yaml          # Package + Bundles + Channels
    └── webhook-operator/
        └── index.yaml          # Package + Bundles + Channels
```

---

## ✅ Warum diese Struktur?

### 1. **OLM File-Based Catalog Standard**

Aus der OLM Dokumentation:

> **Recommended structure:**
> ```
> catalog
> ├── pkgA
> │   └── operator.yaml
> ├── pkgB
> │   └── operator.yaml
> ```
> 
> This layout has the property that **each sub-directory in the directory 
> hierarchy is a self-contained catalog**.

### 2. **Composability**

Einfach Operatoren hinzufügen/entfernen:
```bash
# Neuen Operator aus anderem Catalog kopieren
cp -r other-catalog/fbc/database-operator catalog/fbc/

# Operator entfernen
rm -rf catalog/fbc/old-operator
```

### 3. **OPM lädt rekursiv**

> `opm` loads the catalog by **walking the root directory and recursing 
> into subdirectories**. It attempts to **load every file** it finds.

Das bedeutet:
- ✅ `opm validate catalog/fbc` findet alle `index.yaml` Dateien
- ✅ `opm generate dockerfile catalog/fbc` inkludiert alle Operatoren
- ✅ Jedes Unterverzeichnis ist ein eigenständiger Catalog

---

## 🎯 Beispiel: index.yaml Inhalt

### catalog/fbc/ip-rule-operator/index.yaml:

```yaml
schema: olm.package
name: ip-rule-operator
defaultChannel: stable
description: A Kubernetes operator for managing IP rules
icon:
  base64data: <base64-encoded-logo>
  mediatype: image/svg+xml
---
schema: olm.bundle
name: ip-rule-operator.v0.0.1
package: ip-rule-operator
image: ghcr.io/mariusbertram/ip-rule-operator-bundle:v0.0.1
properties:
  - type: olm.package
    value:
      packageName: ip-rule-operator
      version: 0.0.1
---
schema: olm.channel
package: ip-rule-operator
name: stable
entries:
  - name: ip-rule-operator.v0.0.1
---
schema: olm.channel
package: ip-rule-operator
name: alpha
entries:
  - name: ip-rule-operator.v0.0.1
```

Jedes `index.yaml` enthält **nur** die Objekte für diesen einen Operator!

---

## 💻 Lokale Entwicklung

### Makefile Commands:

```bash
make generate    # Kombiniert, rendert UND splitted FBC
make validate    # Validiert alle Operator-Verzeichnisse
make build       # Baut Catalog-Image
```

### Manuell:

```bash
# 1. Templates kombinieren
python3 scripts/combine-templates.py

# 2. FBC rendern
opm alpha render-template basic catalog/catalog-template.yaml > /tmp/rendered-fbc.yaml

# 3. In Unterverzeichnisse splitten
python3 scripts/split-fbc.py /tmp/rendered-fbc.yaml catalog/fbc

# 4. Struktur prüfen
find catalog/fbc -name "*.yaml"

# 5. Validieren
opm validate catalog/fbc
```

---

## 🧪 Pipeline-Output

### Erfolgreiche Generierung:

```
=== Rendering FBC from Basic Template ===
✓ FBC rendered

=== Splitting FBC into operator directories ===
  ✓ Created ip-rule-operator/index.yaml with 4 objects
  ✓ Created webhook-operator/index.yaml with 6 objects

✓ Split FBC into 2 operator directories

=== FBC Structure ===
catalog/fbc/ip-rule-operator/index.yaml
catalog/fbc/webhook-operator/index.yaml

=== Operator Summary ===
Operator: ip-rule-operator
  Objects: 4
       1 schema: olm.package
       1 schema: olm.bundle
       2 schema: olm.channel

Operator: webhook-operator
  Objects: 6
       1 schema: olm.package
       2 schema: olm.bundle
       3 schema: olm.channel
```

---

## ✅ Vorteile

### 1. **Standard-konform**
- ✅ Folgt OLM File-Based Catalog Empfehlungen
- ✅ Jedes Unterverzeichnis ist ein eigenständiger Catalog

### 2. **Composability**
- ✅ Einfach Operatoren kopieren/löschen
- ✅ Operatoren aus verschiedenen Quellen kombinieren

### 3. **Self-Contained**
- ✅ Jeder Operator kann einzeln validiert werden
- ✅ Teilweise Catalogs möglich

### 4. **OPM-kompatibel**
- ✅ `opm validate` funktioniert
- ✅ `opm generate dockerfile` funktioniert
- ✅ `opm serve` funktioniert

---

## 📚 Referenzen

- **[File-Based Catalogs](docs/file-based-catalogs.md)** - OLM Dokumentation
- **[OPM Template Migration](docs/opm-template-migration.md)** - Template-Workflow
- **[Final Working Workflow](docs/final-working-workflow.md)** - Kompletter Workflow

---

## 🎉 Zusammenfassung

**Vorher:**
- ❌ Alle Operatoren in `catalog/fbc/catalog.yaml`
- ❌ Nicht OLM-Standard-konform
- ❌ Schwer zu komponieren

**Nachher:**
- ✅ Jeder Operator in `catalog/fbc/<operator>/index.yaml`
- ✅ OLM File-Based Catalog Standard
- ✅ Einfach zu komponieren und warten

---

**Status:** ✅ **Implementiert und getestet**  
**Workflow:** OPM Templates → Render → Split → Validate → Build  
**Struktur:** Standard-konform mit separaten Operator-Verzeichnissen
