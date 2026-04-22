# Migration auf Semver Template

## ✅ System auf Semver Template umgestellt!

Das System unterstützt jetzt **sowohl Basic als auch Semver Templates** für maximale Flexibilität.

---

## 🎯 Was wurde geändert?

### 1. Scripts

**`combine-templates.py`:**
- ✅ Unterstützt jetzt `olm.template.basic` UND `olm.semver`
- ✅ Kombiniert beide Template-Typen in eine Datei
- ✅ Zeigt Bundle-Count für semver Templates

### 2. GitHub Actions Workflow

**Render-Step aktualisiert:**
```yaml
# Rendert BEIDE Template-Typen
opm alpha render-template basic catalog/catalog-template.yaml > /tmp/rendered-basic.yaml
opm alpha render-template semver catalog/catalog-template.yaml > /tmp/rendered-semver.yaml

# Kombiniert Outputs
cat /tmp/rendered-basic.yaml /tmp/rendered-semver.yaml > /tmp/rendered-fbc.yaml
```

### 3. Makefile

Lokales `make generate` versucht beide Template-Typen zu rendern.

### 4. operator.yaml Beispiele

**ip-rule-operator:** Konvertiert zu semver Template
**webhook-operator:** Bleibt basic Template (Demo für beide Typen)

---

## 📝 Template-Typen

### Semver Template - Für mehrere Versionen

**Vorteile:**
- ✅ Automatische Channel-Generierung
- ✅ Semver-basierte Upgrade-Pfade
- ✅ Weniger Code für viele Versionen

**Format:**
```yaml
schema: olm.semver
name: operator-name
defaultChannel: stable
description: Description

GenerateMajorChannels: true
GenerateMinorChannels: true

Stable:
  Bundles:
    - Image: ghcr.io/org/operator:v1.0.0
    - Image: ghcr.io/org/operator:v1.1.0
    - Image: ghcr.io/org/operator:v2.0.0
```

**OPM generiert:**
- `stable` - Neueste stabile Version
- `stable-v1` - Neueste v1.x
- `stable-v2` - Neueste v2.x
- `stable-v1.0`, `stable-v1.1` - Wenn GenerateMinorChannels: true

### Basic Template - Für volle Kontrolle

**Vorteile:**
- ✅ Manuelle Channel-Definitionen
- ✅ Explizite Upgrade-Pfade
- ✅ Einfach für wenige Versionen

**Format:**
```yaml
schema: olm.template.basic
entries:
  - schema: olm.package
    name: operator-name
    defaultChannel: stable
    description: Description
  
  - schema: olm.channel
    package: operator-name
    name: stable
    entries:
      - name: operator-name.v1.0.0
      - name: operator-name.v1.1.0
        replaces: operator-name.v1.0.0
  
  - schema: olm.bundle
    image: ghcr.io/org/operator:v1.0.0
  - schema: olm.bundle
    image: ghcr.io/org/operator:v1.1.0
```

---

## 🔄 Workflow

```
operator.yaml (basic ODER semver)
  ↓
combine-templates.py
  → catalog-template.yaml (beide Typen kombiniert)
  ↓
opm alpha render-template basic + semver
  → Rendered FBC (alle Operatoren)
  ↓
split-fbc.py
  → catalog/fbc/<operator>/index.yaml
```

---

## 💻 Mehrere Versionen hinzufügen

### Mit Semver Template:

```yaml
schema: olm.semver
name: my-operator
defaultChannel: stable
description: My operator

GenerateMajorChannels: true

Stable:
  Bundles:
    - Image: ghcr.io/org/my-operator:v1.0.0
    - Image: ghcr.io/org/my-operator:v1.1.0
    - Image: ghcr.io/org/my-operator:v1.2.0  # Neue Version hinzufügen
    - Image: ghcr.io/org/my-operator:v2.0.0
```

**Das ist alles!** OPM generiert automatisch:
- Upgrade-Pfad: v1.0.0 → v1.1.0 → v1.2.0 → v2.0.0
- Channels: stable, stable-v1, stable-v2

### Mit Basic Template:

```yaml
- schema: olm.channel
  package: my-operator
  name: stable
  entries:
    - name: my-operator.v1.0.0
    - name: my-operator.v1.1.0
      replaces: my-operator.v1.0.0
    - name: my-operator.v1.2.0
      replaces: my-operator.v1.1.0  # Manuell definieren
    - name: my-operator.v2.0.0
      replaces: my-operator.v1.2.0
      skipRange: ">=1.0.0 <2.0.0"

- schema: olm.bundle
  image: ghcr.io/org/my-operator:v1.2.0  # Bundle hinzufügen
```

---

## 🎓 Empfehlungen

### Nutze Semver Template wenn:
- ✅ Du mehrere Versionen hast (>3)
- ✅ Du Semver-Regeln folgst
- ✅ Du automatische Channels willst

### Nutze Basic Template wenn:
- ✅ Du nur wenige Versionen hast (1-3)
- ✅ Du spezielle Upgrade-Logik brauchst
- ✅ Du volle Kontrolle über Channels willst

### Beide gleichzeitig?
✅ **Ja!** Du kannst verschiedene Operatoren mit verschiedenen Templates im selben Catalog haben.

---

## 📊 Beispiel: Gemischter Catalog

```
catalog/
├── ip-rule-operator/
│   └── operator.yaml         # schema: olm.semver
├── webhook-operator/
│   └── operator.yaml         # schema: olm.template.basic
└── database-operator/
    └── operator.yaml         # schema: olm.semver
```

Alle werden korrekt kombiniert und gerendert! ✅

---

## ✅ Migration Guide

### Existierenden Operator auf Semver umstellen:

**Vorher (Basic):**
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
      - name: my-operator.v0.0.1
  - schema: olm.bundle
    image: ghcr.io/org/my-operator:v0.0.1
```

**Nachher (Semver):**
```yaml
schema: olm.semver
name: my-operator
defaultChannel: stable
description: My operator

GenerateMajorChannels: true
Stable:
  Bundles:
    - Image: ghcr.io/org/my-operator:v0.0.1
```

**Viel einfacher!** 🎉

---

## 🚀 Nächste Schritte

1. **Teste lokal:**
   ```bash
   make generate
   make validate
   ```

2. **Commit:**
   ```bash
   git add catalog/ scripts/ .github/ README.md CONTRIBUTING.md
   git commit -m "Add Semver template support"
   git push
   ```

3. **Füge weitere Versionen hinzu:**
   ```yaml
   Stable:
     Bundles:
       - Image: ghcr.io/org/operator:v1.0.0
       - Image: ghcr.io/org/operator:v1.1.0  # Einfach hinzufügen!
   ```

---

**Das System ist jetzt flexibler und unterstützt beide Template-Typen!** 🎉
