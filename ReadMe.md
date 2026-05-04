# Th3Sr1b3Pr0j3ct

Gestionnaire de **référentiels conceptuels** implémentant un modèle à quatre couches dédié à la consolidation progressive du sens des concepts.

**Auteur métier** : Bernard Chabot  
**Itération** : 1  
**Stack** : Python 3.11+ · rdflib · Streamlit · pytest  

---

## Architecture en quatre couches

```
┌──────────────────────────────────────────────────────────────┐
│  Couche 4 — RAISONNEMENT  (itération 3)                      │
├──────────────────────────────────────────────────────────────┤
│  Couche 3 — PROVENANCE & ÉVOLUTION  (statuts actifs)         │
├──────────────────────────────────────────────────────────────┤
│  Couche 2 — ASSERTIONS                                       │
│              ├─ Descriptions intrinsèques (SKOS)             │
│              ├─ Relations à d'autres entités                 │
│              ├─ Actes de représentation (récursifs)          │
│              └─ Mappings inter-référentiels                  │
├──────────────────────────────────────────────────────────────┤
│  Couche 1 — IDENTITÉ  (urn:concept:scribe:{uuid}#vN)         │
└──────────────────────────────────────────────────────────────┘
```

### Principe de récursion sujet/objet

Toute entité peut, selon le contexte, jouer le rôle de **sujet** (l'entité représentée) ou d'**objet** (la représentation elle-même). La distinction est contextuelle et non intrinsèque. La récursion est non bornée :

```
Usine de Marseille → représentée par → Maquette → représentée par → Plan → représentée par → Photo
```

Chaque étape de la chaîne est une entité indépendante, documentable, avec son propre identifiant opaque. Cette architecture suit les principes de la sémiose illimitée de Peirce et du modèle CIDOC-CRM (ISO 21127).

---

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/MyShivaRepo/Th3Scr1b3Pr0j3ct.git
cd Th3Scr1b3Pr0j3ct

# Créer un environnement virtuel et installer les dépendances
uv venv
uv pip install -e ".[dev]"
```

Ou avec `pip` :

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"
```

---

## Lancement

```bash
streamlit run src/ui/app.py
```

L'application s'ouvre dans le navigateur sur `http://localhost:8501`.  
Les 12 entités du référentiel initial sont chargées automatiquement au premier démarrage.

---

## Tests

```bash
pytest
```

Pour la couverture :

```bash
pytest --cov=src --cov-report=term-missing
```

---

## Structure des fichiers

```
Th3Sr1b3Pr0j3ct/
├── src/
│   ├── model/
│   │   ├── identity.py          # Couche 1 — URI opaques
│   │   ├── assertions.py        # Couche 2 — descriptions, relations, mappings
│   │   ├── representation.py    # Couche 2.3.3 — actes de représentation
│   │   └── concept.py           # Modèle d'entité
│   ├── storage/
│   │   └── turtle_store.py      # Persistance RDF Turtle (rdflib)
│   ├── ui/
│   │   ├── app.py               # Application Streamlit
│   │   └── views/               # Vues : liste, création, édition, représentations
│   └── seed/
│       └── load_concepts.py     # Chargement du référentiel initial
├── data/
│   ├── concepts.ttl             # Stockage principal (généré)
│   └── seed/
│       └── bernard_concepts.ttl # 12 entités initiales
├── tests/                       # Tests pytest
└── requirements/
    └── spec-iteration-1.md      # Spécification v1.1
```

---

## Format des identifiants (Couche 1)

```
urn:concept:scribe:{UUID-v4}#{version}
```

Exemple :
```
urn:concept:scribe:7B3F2A91-D4E8-4C5B-9F12-A3D7E891B2C4#v1
```

- L'identifiant est **opaque** : il ne contient aucune information sémantique
- Il est **persistant** : jamais réutilisé, même après suppression
- La **version** est incrémentée à chaque modification (`v1` → `v2`)
- Sans fragment `#version`, l'URI désigne la **lignée** (toutes versions)

---

## Vocabulaires RDF utilisés

| Préfixe | Namespace |
|---------|-----------|
| `skos:` | `http://www.w3.org/2004/02/skos/core#` |
| `owl:`  | `http://www.w3.org/2002/07/owl#` |
| `xsd:`  | `http://www.w3.org/2001/XMLSchema#` |
| `scribe:` | `urn:scribe:vocabulary#` |

---

## Feuille de route

- **Itération 2** : Visualisation graphe interactif · Fusion/scission · PROV-O
- **Itération 3** : Validation SHACL · Règles SWRL · Recherche sémantique · Embeddings
- **Itération 4+** : Intégration LLM via MCP · Mappings Wikidata
