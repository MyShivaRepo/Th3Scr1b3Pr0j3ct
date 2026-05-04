# Th3Sr1b3Pr0j3ct — Spécification de l'itération 1

**Version** : 1.1
**Date** : 2026-05-01
**Auteur métier** : Bernard Chabot
**Statut** : À implémenter

**Note de version 1.1** : intégration de la dimension récursive sujet/objet (sections 2.3, 3.2.5, 5, 8.4). Aucun élargissement du périmètre fonctionnel par rapport à la v1.0.

---

## 1. Contexte et finalité du projet

### 1.1 Origine du projet

Th3Sr1b3Pr0j3ct (*The Scribe Project*) est une application de gestion de **référentiels conceptuels** qui implémente un modèle architectural à **quatre couches** dédié à la consolidation progressive du sens des concepts.

Ce modèle est issu d'une réflexion croisant plusieurs traditions :

- **Web Sémantique** (W3C : RDF, OWL, SKOS, SPARQL, SHACL, PROV-O)
- **Ingénierie des connaissances** (cadres REAF et KRVF de Bernard Chabot)
- **Approche neuro-symbolique** (NeSy AI — communauté Hitzler, Garcez, Kautz)
- **Sémantique distributionnelle** (Wittgenstein, Harris, Firth)
- **Sémiotique pragmatique** (Peirce, Buckland) et **modélisation patrimoniale** (CIDOC-CRM, FRBR)

Le projet vise à concilier deux exigences souvent perçues comme contradictoires :

1. **Séduction conceptuelle** : un sens qui émerge progressivement par accumulation d'assertions multimodales, dans le respect de la nature récursive et contextuelle de la relation sujet/objet
2. **Réalisme pratique** : des outils éprouvés, des standards W3C, une scalabilité industrielle

### 1.2 Problématique adressée

Les approches existantes de gestion de concepts présentent chacune des limitations :

- Les **URI W3C** confondent souvent identifiant et description ; ne gèrent pas nativement l'évolution
- Les **identifiants par hash** (InfoCentral, IPFS) cassent quand le contenu évolue
- Les **systèmes purement vectoriels** perdent la composabilité formelle et l'auditabilité
- Les **ontologies OWL classiques** peinent à intégrer les représentations non-symboliques (images, embeddings)
- **La plupart des modèles** confondent sujet et objet en aplatissant la hiérarchie représentationnelle, ce qui détruit l'information sur les actes de représentation eux-mêmes

Th3Sr1b3Pr0j3ct propose une articulation rigoureuse en quatre couches qui sépare strictement :

- **Ce qui identifie** une entité (couche 1)
- **Ce qui la décrit, la relie, la représente** (couche 2)
- **Ce qui trace son évolution** (couche 3)
- **Ce qui en valide la cohérence** (couche 4)

### 1.3 Principes fondateurs

> **Principe 1** : Une entité est définie par l'**accumulation progressive et évolutive** de ses assertions, pivotées autour d'un identifiant strictement opaque et persistant.

> **Principe 2** : La distinction **sujet / objet** n'est pas une propriété intrinsèque des entités, mais une **fonction contextuelle** qu'elles assument dans des actes de représentation. Toute entité peut, selon le contexte, jouer le rôle de sujet ou d'objet — y compris simultanément.

Le sens n'est jamais fixé a priori. Il se consolide. L'identifiant reste stable. Tout le reste évolue. Et toute représentation est elle-même une entité documentable à part entière.

---

## 2. Le modèle à quatre couches

### 2.1 Vue d'ensemble

```
┌──────────────────────────────────────────────────────────────┐
│  Couche 4 — RAISONNEMENT  (validation, inférence)            │
├──────────────────────────────────────────────────────────────┤
│  Couche 3 — PROVENANCE & ÉVOLUTION  (événements immuables)   │
├──────────────────────────────────────────────────────────────┤
│  Couche 2 — ASSERTIONS  (toutes contributions au sens)       │
│              ├─ Descriptions intrinsèques                    │
│              ├─ Relations à d'autres entités                 │
│              ├─ Actes de représentation (récursifs)          │
│              ├─ Mappings inter-référentiels                  │
│              └─ Représentations apprises (embeddings)        │
├──────────────────────────────────────────────────────────────┤
│  Couche 1 — IDENTITÉ  (URI opaque, persistant, versionné)    │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Couche 1 — Identité

**Principe** : chaque entité conceptuelle reçoit un et un seul identifiant, strictement opaque, persistant, versionné.

**Format de l'identifiant** :

```
urn:concept:{namespace}:{conceptId}#{version}
```

Exemple :

```
urn:concept:scribe:7B3F2A91-D4E8-4C5B-9F12-A3D7E891B2C4#v1
```

**Composants** :

| Composant       | Rôle                              | Implémentation                       |
|-----------------|-----------------------------------|--------------------------------------|
| `urn:concept:`  | Préfixe normalisant               | Constante                            |
| `{namespace}`   | Autorité de gestion               | Pour cette itération : `scribe`      |
| `{conceptId}`   | UUID                              | UUID v4 (génération distribuée)      |
| `#{version}`    | Version courante                  | `v1`, `v2`, ... (incrémenté)         |

**Règles invariables** :

- Un identifiant attribué n'est **jamais réutilisé**, même si l'entité est supprimée/dépréciée
- Un identifiant ne **change jamais** de signification au fil du temps
- Sans `#version`, l'URI désigne **la lignée** de l'entité (toutes versions confondues)
- Avec `#version`, l'URI désigne **un état figé** à un instant donné
- **Toute entité documentable reçoit son propre identifiant** — y compris les représentations qui en sont elles-mêmes documentables (cf. principe 2 et section 2.3.3)

### 2.3 Couche 2 — Assertions

**Principe** : tout ce qui contribue au sens d'une entité est une **assertion**, traitée uniformément quelle que soit sa nature.

#### 2.3.1 Descriptions intrinsèques

Assertions qui décrivent l'entité en elle-même, sans référence à une autre entité.

| Type                | Vocabulaire RDF              | Cardinalité | Exemple                                      |
|---------------------|------------------------------|-------------|----------------------------------------------|
| Label préféré       | `skos:prefLabel`             | 1 par langue | `"Knowledge Representation Visualization Framework"@en` |
| Label alternatif    | `skos:altLabel`              | n par langue | `"KRVF"@en`                                  |
| Définition          | `skos:definition`            | 1 par langue | `"Framework méthodologique..."@fr`           |
| Note                | `skos:note`, `skos:scopeNote` | n          | Notes explicatives diverses                  |

**Règle importante (révision v1.1)** : les propriétés `:hasImage`, `:hasDocument`, `:hasExternalLink` qui figuraient en v1.0 ont été **supprimées**. Une image, un document ou une ressource externe sont des entités à part entière qui doivent être modélisées comme des entités possédant leur propre identifiant, et reliées à l'entité de base par un acte de représentation (section 2.3.3).

#### 2.3.2 Relations à d'autres entités

Assertions qui placent l'entité dans le réseau sémantique.

| Type                | Vocabulaire RDF              | Sémantique                                    |
|---------------------|------------------------------|-----------------------------------------------|
| Concept plus large  | `skos:broader`               | Relation hiérarchique vers parent             |
| Concept plus étroit | `skos:narrower`              | Relation hiérarchique vers enfant             |
| Concept relié       | `skos:related`               | Relation associative non hiérarchique         |
| Précède             | `:precedes`                  | Relation temporelle/logique                   |
| Implique            | `:implies`                   | Relation logique forte                        |
| Compose             | `:isPartOf` / `:hasPart`     | Relation méréologique                         |

#### 2.3.3 Actes de représentation (dimension récursive)

**Principe directeur** : la distinction sujet/objet est contextuelle. Toute entité peut, selon le contexte, être l'**objet** (la représentation) d'une autre entité, et le **sujet** (le représenté) d'une troisième entité. La récursion est non bornée.

**Exemple canonique** :

```
Usine de Marseille  ──représentée par──▶  Maquette de l'usine
                                                  │
                                                  └──représentée par──▶  Plan de la maquette
                                                                                  │
                                                                                  └──représentée par──▶  Photo du plan
```

Chaque entité de cette chaîne est :

- Un **objet** dans la relation au-dessus
- Un **sujet** dans la relation en-dessous
- Documentable et identifiable indépendamment

**Modélisation** : la relation `:isRepresentedBy` (et son inverse `:represents`) pointe **toujours vers une autre entité** dotée de son propre identifiant opaque. Les métadonnées du lien sont portées par un nœud d'assertion intermédiaire.

**Schéma RDF (avec nœud blanc d'assertion)** :

```turtle
:UsineMarseille     a :Concept ;
                    skos:prefLabel "Usine de traitement des eaux de Marseille"@fr ;
                    :isRepresentedBy [
                        :representation        :MaquetteUsine ;
                        :representationKind    :PhysicalScaleModel ;
                        :representationContext "Présentation portes ouvertes 1990"@fr ;
                        :representationCreatedBy "Atelier de maquettes Dupont"@fr ;
                        :representationCreatedOn "1987-03-15"^^xsd:date
                    ] .

:MaquetteUsine      a :Concept ;                   # ← entité à part entière
                    skos:prefLabel "Maquette de l'usine de Marseille"@fr ;
                    :isRepresentedBy [
                        :representation        :PlanMaquette ;
                        :representationKind    :TechnicalDrawing ;
                        :representationCreatedBy "Bureau d'études X"@fr ;
                        :representationCreatedOn "1990-06-22"^^xsd:date
                    ] .

:PlanMaquette       a :Concept ;                   # ← entité à part entière
                    skos:prefLabel "Plan de la maquette"@fr .
```

**Types de représentations attendus** (`:representationKind`) :

| Valeur                       | Description                                        |
|------------------------------|----------------------------------------------------|
| `:PhysicalScaleModel`        | Maquette physique                                  |
| `:TechnicalDrawing`          | Plan, schéma technique                             |
| `:Photograph`                | Photographie                                       |
| `:DigitalImage`              | Image numérique                                    |
| `:Video`                     | Vidéo                                              |
| `:AudioRecording`            | Enregistrement audio                               |
| `:Document`                  | Document texte                                     |
| `:WebResource`               | Ressource web (page, article)                      |
| `:Diagram`                   | Diagramme conceptuel                               |
| `:DigitalTwin3D`             | Modèle 3D / jumeau numérique                       |
| `:Embedding`                 | Représentation vectorielle apprise (itération 3)   |

**Règle de modélisation** : ne **jamais** modéliser une représentation comme une simple chaîne de caractères ou une URL portée comme propriété directe. Toujours créer une entité concept dédiée et la relier via un acte de représentation. Cette discipline préserve la possibilité de documenter ultérieurement la représentation elle-même (auteur, date, droits, contexte de création, ses propres représentations dérivées, etc.).

**Fondements théoriques de cette approche** :

- Sémiose illimitée de **Peirce** (toute interprétation peut elle-même être interprétée)
- Modèle CIDOC-CRM (`P138 represents`, `E13 Attribute Assignment`) — standard ISO 21127 du monde patrimonial
- Modèle FRBR (Œuvre / Expression / Manifestation / Item) — bibliothéconomie
- Théorie de l'**information-as-thing** de Buckland (1991)

#### 2.3.4 Mappings inter-référentiels

Assertions qui relient l'entité à des entités d'autres référentiels.

| Type                | Vocabulaire RDF              | Sémantique                                    |
|---------------------|------------------------------|-----------------------------------------------|
| Identité stricte    | `skos:exactMatch`            | Concept identique dans un autre référentiel   |
| Identité approximative | `skos:closeMatch`         | Concept très proche                           |
| Concept générique   | `skos:broadMatch`            | Concept plus large dans autre référentiel     |
| Concept spécifique  | `skos:narrowMatch`           | Concept plus étroit dans autre référentiel    |
| Identité OWL        | `owl:sameAs`                 | Identité formelle au sens OWL                 |

**Métadonnées de qualification** (pour chaque mapping) :

- Confiance (`:hasConfidence`, valeur entre 0.0 et 1.0)
- Agent ayant validé (`:wasMappedBy`)
- Date du mapping (`:wasMappedOn`)

#### 2.3.5 Représentations apprises (embeddings)

**Note pour l'itération 1** : prévu structurellement, **non implémenté** dans cette itération. Les embeddings seront ajoutés en itération 2 ou 3.

Conformément au principe 2, un embedding est lui-même une entité conceptuelle dotée d'un identifiant — pas une propriété directe. Cela permet de documenter le modèle qui l'a généré, sa version, ses dimensions, et de gérer son évolution au fil des changements de modèles.

### 2.4 Couche 3 — Provenance & Évolution

**Principe** : chaque modification d'une entité est un événement immuable, daté, qui s'ajoute sans jamais effacer le passé.

**Note pour l'itération 1** : prévu structurellement (statuts explicites, traces basiques de modification), **fusion/scission non implémentées**. La gestion complète des événements PROV-O sera développée en itération 2.

**Statuts pris en charge dès l'itération 1** :

| Statut         | Signification                                                  |
|----------------|----------------------------------------------------------------|
| `:Active`      | Entité courante utilisable                                     |
| `:Provisional` | Entité en cours de définition, non stabilisée                  |
| `:Deprecated`  | Entité dépréciée sans remplaçant                               |

Les statuts `:MergedInto`, `:SplitInto`, `:Superseded` seront introduits en itération 2.

### 2.5 Couche 4 — Raisonnement

**Note pour l'itération 1** : prévu structurellement, **non implémenté**. Les validations SHACL et règles SWRL seront introduites en itération 3.

---

## 3. Périmètre fonctionnel de l'itération 1

### 3.1 Fonctionnalité unique : Création/édition de concepts

L'itération 1 implémente **strictement** la fonctionnalité de création et d'édition d'entités conceptuelles, démontrant les couches 1 et 2 du modèle (incluant la dimension récursive sujet/objet).

### 3.2 Cas d'usage détaillés

#### 3.2.1 Créer une nouvelle entité conceptuelle

**Acteur** : utilisateur métier (Bernard Chabot)

**Pré-conditions** : aucune

**Déroulement nominal** :

1. L'utilisateur clique sur "Nouvelle entité"
2. Le système génère automatiquement :
   - Un identifiant UUID v4
   - L'URI complète au format `urn:concept:scribe:{uuid}#v1`
   - Le statut initial `:Provisional`
   - L'horodatage de création
3. L'utilisateur saisit au minimum :
   - Un `skos:prefLabel` en français
4. L'utilisateur peut ajouter optionnellement :
   - Un `skos:prefLabel` dans d'autres langues
   - Un ou plusieurs `skos:altLabel`
   - Une `skos:definition`
   - Des notes (`skos:note`, `skos:scopeNote`)
5. L'utilisateur sauvegarde
6. Le système enregistre l'entité

**Critère d'acceptation** :

- L'entité est créée avec un identifiant unique opaque jamais déjà attribué
- Toutes les assertions saisies sont préservées
- L'entité apparaît dans la liste du référentiel

#### 3.2.2 Éditer une entité existante

**Acteur** : utilisateur métier

**Pré-conditions** : au moins une entité existe

**Déroulement nominal** :

1. L'utilisateur sélectionne une entité dans la liste
2. Le système affiche toutes les assertions de l'entité
3. L'utilisateur peut :
   - Ajouter de nouvelles assertions (de tous types prévus en itération 1)
   - Modifier des assertions existantes
   - Supprimer des assertions existantes
   - Changer le statut de l'entité (Active / Provisional / Deprecated)
4. L'utilisateur sauvegarde
5. Le système :
   - Préserve l'identifiant de l'entité (jamais modifié)
   - Incrémente la version (`v1` → `v2`)
   - Conserve l'horodatage de la modification

**Critère d'acceptation** :

- L'identifiant UUID reste **rigoureusement identique** après édition
- La version est incrémentée
- Les modifications sont visibles dans la liste

#### 3.2.3 Ajouter une relation à une autre entité

**Acteur** : utilisateur métier

**Pré-conditions** : au moins deux entités existent

**Déroulement nominal** :

1. L'utilisateur édite une entité source
2. L'utilisateur ajoute une nouvelle assertion de type relation
3. Il sélectionne le type de relation (`skos:broader`, `skos:narrower`, `skos:related`, etc.)
4. Il sélectionne l'entité cible parmi les entités existantes
5. L'utilisateur sauvegarde
6. Le système enregistre la relation

**Critère d'acceptation** :

- La relation est correctement modélisée comme assertion (couche 2.3.2)
- L'utilisateur peut visualiser les relations entrantes et sortantes de l'entité

#### 3.2.4 Lister et rechercher les entités

**Acteur** : utilisateur métier

**Pré-conditions** : aucune

**Déroulement nominal** :

1. L'utilisateur accède à la liste des entités
2. Le système affiche toutes les entités avec :
   - Le label préféré (en français par défaut)
   - L'identifiant court (8 premiers caractères de l'UUID)
   - Le statut
   - La date de dernière modification
3. L'utilisateur peut filtrer par :
   - Texte dans n'importe quel label
   - Statut

**Critère d'acceptation** :

- Toutes les entités du référentiel sont affichées
- La recherche fonctionne sur tous les labels (préférés, alternatifs, dans toutes langues)

#### 3.2.5 Créer un acte de représentation entre deux entités (NOUVEAU v1.1)

**Acteur** : utilisateur métier

**Pré-conditions** : au moins deux entités existent

**Déroulement nominal** :

1. L'utilisateur édite une entité source (le **sujet** — celui qui sera représenté)
2. L'utilisateur ajoute une nouvelle assertion de type "Acte de représentation"
3. Il sélectionne l'entité cible parmi les entités existantes (l'**objet** — la représentation)
   - Si la représentation n'existe pas encore comme entité, il doit d'abord la créer (cas d'usage 3.2.1) puis revenir
4. Il qualifie l'acte de représentation par :
   - Le type de représentation (`:representationKind`) — sélection dans la liste de la section 2.3.3
   - Le contexte (texte libre, optionnel)
   - L'auteur de la représentation (texte libre, optionnel)
   - La date de création de la représentation (date, optionnel)
5. L'utilisateur sauvegarde
6. Le système enregistre l'acte de représentation comme structure RDF (avec nœud blanc d'assertion) sur l'entité source

**Critère d'acceptation** :

- L'acte de représentation est correctement modélisé selon le schéma de la section 2.3.3
- Le **même** UUID de l'entité cible peut être utilisé comme objet de plusieurs actes de représentation différents (provenant d'entités sources différentes)
- L'entité cible (l'objet) reste **modifiable indépendamment** comme une entité à part entière (elle peut elle-même avoir ses propres représentations, démontrant la récursion)
- L'utilisateur peut visualiser, sur n'importe quelle entité :
  - Les actes de représentation **sortants** (entités qu'elle représente)
  - Les actes de représentation **entrants** (entités qui la représentent)

### 3.3 Fonctionnalités explicitement hors scope de l'itération 1

Les fonctionnalités suivantes sont **conscientes et explicites** comme étant hors périmètre :

- ❌ Visualisation graphe interactif → itération 2
- ❌ Fusion/scission d'entités avec événements → itération 2
- ❌ Recherche sémantique avancée → itération 3
- ❌ Validation par règles SHACL/SWRL → itération 3
- ❌ Embeddings et représentations apprises → itération 3
- ❌ Intégration LLM → itération ultérieure
- ❌ Multi-utilisateurs et gestion des droits → non prévu
- ❌ Authentification → non prévu
- ❌ Synchronisation cloud → non prévu

---

## 4. Choix techniques recommandés

### 4.1 Stack technique

| Composant            | Technologie recommandée               | Justification                                                  |
|----------------------|---------------------------------------|----------------------------------------------------------------|
| Langage backend      | **Python 3.11+**                      | Maturité, écosystème Web Sémantique excellent (rdflib)        |
| Manipulation RDF     | **rdflib**                            | Bibliothèque de référence Python pour RDF/OWL                  |
| Stockage             | **Fichier Turtle local** (`.ttl`)     | Simplicité, lisibilité humaine, pas d'infrastructure          |
| Génération UUID      | **module `uuid` standard** (uuid4)    | Standard Python, pas de dépendance                             |
| Interface utilisateur | **Streamlit**                        | Rapide à développer, idéal pour MVP, déployable localement    |
| Tests                | **pytest**                            | Standard Python                                                |
| Gestion dépendances  | **`uv`** ou **`pip` + venv**          | Au choix du développeur                                        |

**Note** : Streamlit est recommandé pour l'itération 1 (rapidité, simplicité). Une migration vers Flask ou FastAPI sera envisagée en itération 2 ou 3 si nécessaire.

### 4.2 Structure de fichiers attendue

```
Th3Sr1b3Pr0j3ct/
├── README.md                     # Présentation du projet
├── exigences/
│   └── spec-iteration-1.md       # Ce document
├── pyproject.toml                # Configuration projet et dépendances
├── src/
│   ├── __init__.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── identity.py           # Couche 1 — Génération et gestion des URI
│   │   ├── assertions.py         # Couche 2 — Modèle des assertions
│   │   ├── representation.py     # Couche 2.3.3 — Actes de représentation (NOUVEAU v1.1)
│   │   └── concept.py            # Modèle d'entité articulant les couches
│   ├── storage/
│   │   ├── __init__.py
│   │   └── turtle_store.py       # Persistance fichier Turtle
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py                # Application Streamlit principale
│   │   ├── views/
│   │   │   ├── concept_list.py   # Liste et recherche des entités
│   │   │   ├── concept_edit.py   # Édition d'une entité
│   │   │   ├── concept_create.py # Création d'une nouvelle entité
│   │   │   └── representation_edit.py # Édition d'actes de représentation (NOUVEAU v1.1)
│   └── seed/
│       ├── __init__.py
│       └── load_concepts.py      # Chargement du référentiel initial
├── data/
│   ├── concepts.ttl              # Fichier de stockage principal
│   └── seed/
│       └── bernard_concepts.ttl  # Référentiel initial pré-chargé
├── tests/
│   ├── __init__.py
│   ├── test_identity.py
│   ├── test_assertions.py
│   ├── test_representation.py    # NOUVEAU v1.1
│   ├── test_storage.py
│   └── test_concept.py
└── .gitignore
```

### 4.3 Conventions de code

- **PEP 8** strict
- **Type hints** systématiques
- **Docstrings** en français pour les fonctions publiques
- **Commentaires** parcimonieux mais éclairants quand le code n'est pas évident
- **Tests unitaires** pour la couche modèle (au minimum) et la couche stockage

---

## 5. Référentiel initial pré-chargé

Le projet est livré avec un mini-référentiel initial de **12 entités** issues de la pratique professionnelle de Bernard Chabot, dont **2 entités illustrent explicitement la récursion sujet/objet** (révision v1.1).

### 5.1 Liste des entités initiales

| #  | Entité                  | Type             | Statut       | Label préféré FR                                          |
|----|-------------------------|------------------|--------------|-----------------------------------------------------------|
| 1  | xLM                     | Concept          | Active       | eXtended Lifecycle Management                             |
| 2  | KRVF                    | Concept          | Active       | Knowledge Representation & Visualization Framework        |
| 3  | REAF                    | Concept          | Active       | Reference Enterprise Architecture Framework               |
| 4  | PLM                     | Concept          | Active       | Product Lifecycle Management                              |
| 5  | Ontologie OWL           | Concept          | Active       | Ontologie OWL                                             |
| 6  | Règles SWRL             | Concept          | Active       | Règles métier SWRL                                        |
| 7  | XAI                     | Concept          | Active       | Intelligence artificielle explicable (XAI)                |
| 8  | Web Sémantique          | Concept          | Active       | Web Sémantique                                            |
| 9  | Invariant métier        | Concept          | Active       | Invariant métier                                          |
| 10 | Ingénierie connaissances| Concept          | Active       | Ingénierie des connaissances                              |
| 11 | Document xLM_FR         | Représentation   | Active       | Document de présentation du concept xLM (français)        |
| 12 | Diagramme KRVF couches  | Représentation   | Active       | Diagramme illustrant les couches de KRVF                  |

### 5.2 Relations attendues entre les entités 1 à 10

À titre indicatif (le développeur les modélisera comme assertions de relation, section 2.3.2) :

- `xLM` `:isExtensionOf` `PLM`
- `xLM` `:articulatesWith` `XAI`
- `xLM` `:usesTechnology` `Ontologie OWL`
- `xLM` `:usesTechnology` `Règles SWRL`
- `KRVF` `:isFrameworkFor` `Ingénierie connaissances`
- `KRVF` `:usesTechnology` `Web Sémantique`
- `REAF` `:isBuiltUpon` `Invariant métier`
- `Ontologie OWL` `:isPartOf` `Web Sémantique`
- `Règles SWRL` `:extendsTechnology` `Ontologie OWL`

### 5.3 Actes de représentation attendus (illustration de la récursion v1.1)

Pour démontrer la dimension récursive sujet/objet introduite en v1.1, le référentiel initial comprend explicitement deux actes de représentation :

#### Acte 1 — xLM représenté par un document

```turtle
:xLM    :isRepresentedBy [
            :representation        :DocumentXLM_FR ;
            :representationKind    :Document ;
            :representationContext "Présentation publique du concept sur GitHub"@fr ;
            :representationCreatedBy "Bernard Chabot" ;
            :representationCreatedOn "2018-09-15"^^xsd:date
        ] .
```

L'entité `:DocumentXLM_FR` (entité #11 de la liste) est elle-même un concept à part entière, dont les assertions intrinsèques peuvent inclure son URL source (https://github.com/iPlumb3r/SEAMLESS/blob/master/Analysis/About_xLM_FR.md), son auteur, sa date, sa langue, etc.

#### Acte 2 — KRVF représenté par un diagramme

```turtle
:KRVF   :isRepresentedBy [
            :representation        :DiagrammeKRVFCouches ;
            :representationKind    :Diagram ;
            :representationContext "Diagramme conceptuel"@fr
        ] .
```

L'entité `:DiagrammeKRVFCouches` (entité #12) est également documentée comme entité indépendante.

**Test de récursion suggéré pour exercer le modèle après installation** : l'utilisateur pourra créer une troisième entité (par exemple `:PhotoDuDiagrammeKRVF`) et l'associer à `:DiagrammeKRVFCouches` via un nouvel acte de représentation, démontrant ainsi la profondeur récursive non bornée.

### 5.4 Définitions attendues

Chaque entité du référentiel initial doit comporter au minimum :

- Un `skos:prefLabel` en français
- Un `skos:prefLabel` en anglais (le cas échéant)
- Une `skos:definition` en français de 2 à 5 phrases
- Au moins une note `skos:scopeNote` ou `skos:note` apportant un éclairage complémentaire

Le contenu textuel de ces définitions est laissé à la rédaction du développeur, en s'appuyant sur les ressources publiques de Bernard Chabot :

- https://github.com/iPlumb3r/About/blob/master/BernardChabot/Bio_FR.md
- https://github.com/iPlumb3r/About/blob/master/BernardChabot/CV_Textual_FR.md
- https://github.com/iPlumb3r/SEAMLESS/blob/master/Analysis/About_xLM_FR.md

---

## 6. Critères d'acceptation globaux de l'itération 1

L'itération 1 sera considérée comme **réussie** si toutes les conditions suivantes sont satisfaites :

### 6.1 Conformité fonctionnelle

- ✅ L'application se lance par une commande simple (ex : `streamlit run src/ui/app.py`)
- ✅ Les 12 entités du référentiel initial sont chargées au démarrage
- ✅ Un utilisateur peut créer une nouvelle entité conforme aux règles de la couche 1
- ✅ Un utilisateur peut éditer une entité existante **sans que son identifiant ne change**
- ✅ Un utilisateur peut ajouter, modifier, supprimer toutes les assertions prévues
- ✅ Un utilisateur peut établir des relations entre entités
- ✅ Un utilisateur peut créer des actes de représentation entre entités (cas d'usage 3.2.5)
- ✅ La liste des entités est consultable et filtrable
- ✅ Le statut d'une entité peut être modifié

### 6.2 Conformité au modèle

- ✅ Les identifiants sont strictement opaques (UUID v4) et préfixés `urn:concept:scribe:`
- ✅ Les identifiants ne sont **jamais** réutilisés ni modifiés
- ✅ Les versions sont gérées correctement (incrément à chaque modification)
- ✅ Le stockage produit un fichier RDF Turtle valide
- ✅ Le fichier Turtle utilise les bons vocabulaires (SKOS, RDF, RDFS, propriétés custom dans un namespace dédié)
- ✅ **Aucune représentation n'est modélisée comme propriété directe** — toujours comme entité à part entière reliée par un acte de représentation (règle issue de la v1.1)
- ✅ La récursion sujet/objet est techniquement supportée à profondeur arbitraire (test : créer une chaîne A → représentée par B → représentée par C → représentée par D)

### 6.3 Conformité technique

- ✅ Code Python 3.11+ avec type hints
- ✅ Tests unitaires couvrent au minimum la couche modèle (`identity.py`, `assertions.py`, `representation.py`, `concept.py`)
- ✅ README explicite avec instructions d'installation et de lancement
- ✅ Aucune dépendance externe au-delà de ce qui est listé dans `pyproject.toml`
- ✅ Le code se lance sur macOS sans configuration particulière

### 6.4 Documentation produite

- ✅ `README.md` à la racine : présentation, installation, lancement, usage de base
- ✅ Docstrings dans les modules `model/`
- ✅ Commentaires éclairants dans les fichiers complexes
- ✅ Section dédiée dans le README expliquant le **principe de récursion sujet/objet** avec un exemple

---

## 7. Feuille de route prévisionnelle

Pour information et pour aider Claude Code à comprendre la trajectoire :

### Itération 2 (à venir)

- Visualisation interactive du graphe des entités (incluant les actes de représentation)
- Fusion et scission d'entités avec événements PROV-O
- Statuts étendus (`:MergedInto`, `:SplitInto`, `:Superseded`)
- Historique complet des modifications
- Affichage spécifique des chaînes récursives de représentation

### Itération 3 (à venir)

- Validation par règles SHACL
- Règles SWRL pour la cohérence métier
- Recherche sémantique
- Génération d'embeddings (sentence-transformers) — modélisés comme entités selon le principe 2
- Base vectorielle adjacente

### Itération 4+ (à explorer)

- Intégration LLM via MCP
- Mappings inter-référentiels (alignement avec Wikidata, par exemple)
- Notifications LDN
- Multi-utilisateurs

---

## 8. Annexes

### 8.1 Glossaire

| Terme              | Définition                                                                |
|--------------------|---------------------------------------------------------------------------|
| **Acte de représentation** | Assertion typée qui établit un lien sujet → objet entre deux entités, qualifié par un type (`:representationKind`), un contexte, un auteur, une date |
| **Assertion**      | Affirmation portée sur une entité qui contribue à son sens                |
| **Concept / Entité conceptuelle** | Entité identifiée par un URI opaque, enrichie par des assertions. Toute entité documentable est traitée comme un concept |
| **KRVF**           | Knowledge Representation & Visualization Framework                        |
| **Objet (au sens sujet/objet)** | Rôle joué par une entité quand elle représente une autre entité |
| **OWL**            | Web Ontology Language (W3C)                                              |
| **PLM**            | Product Lifecycle Management                                              |
| **PROV-O**         | Provenance Ontology (W3C)                                                |
| **RDF**            | Resource Description Framework (W3C)                                      |
| **REAF**           | Reference Enterprise Architecture Framework                               |
| **Récursion sujet/objet** | Propriété selon laquelle toute entité peut, selon le contexte, jouer le rôle de sujet ou d'objet — y compris simultanément |
| **SHACL**          | Shapes Constraint Language (W3C)                                          |
| **SKOS**           | Simple Knowledge Organization System (W3C)                                |
| **Sujet (au sens sujet/objet)** | Rôle joué par une entité quand elle est représentée par une autre entité |
| **SWRL**           | Semantic Web Rule Language (W3C)                                          |
| **xLM**            | eXtended Lifecycle Management                                             |

### 8.2 Vocabulaires RDF utilisés

- `rdf:` → `http://www.w3.org/1999/02/22-rdf-syntax-ns#`
- `rdfs:` → `http://www.w3.org/2000/01/rdf-schema#`
- `owl:` → `http://www.w3.org/2002/07/owl#`
- `skos:` → `http://www.w3.org/2004/02/skos/core#`
- `prov:` → `http://www.w3.org/ns/prov#`
- `xsd:` → `http://www.w3.org/2001/XMLSchema#`
- `:` (vocabulaire local) → `urn:scribe:vocabulary#`

### 8.3 Note pour Claude Code

Cette spécification est **suffisante** pour implémenter l'itération 1 sans nécessiter de contexte conversationnel additionnel. En cas de doute :

1. Privilégier la **simplicité** sur la complétude (c'est un MVP)
2. Privilégier les **standards W3C** sur les solutions custom
3. Privilégier la **clarté du code** sur la performance
4. Documenter dans le code toute décision non triviale

Pour toute question d'interprétation, consulter en priorité :
- La section 2 (modèle à 4 couches) pour les principes architecturaux
- La section 2.3.3 spécifiquement pour la récursion sujet/objet, qui est un point distinctif du modèle
- La section 3 (cas d'usage détaillés) pour les comportements attendus
- La section 6 (critères d'acceptation) pour les invariants à respecter

### 8.4 Fondements théoriques de la récursion sujet/objet (v1.1)

Pour le développeur qui souhaite comprendre la profondeur du choix architectural, cette annexe rassemble les principales références philosophiques et techniques.

**Sémiotique pragmatique** :

- **Charles Sanders Peirce** (1839-1914) — Théorie de la sémiose illimitée. Toute interprétation est elle-même un signe susceptible d'être interprété. Le sens n'est jamais clos.
- **Michael Buckland** (1991) — *« Information as Thing »*. L'information n'est pas une catégorie ontologique séparée des objets : c'est une fonction qu'une chose assume contextuellement.

**Standards de modélisation** :

- **CIDOC-CRM** (ISO 21127) — Ontologie patrimoniale qui distingue rigoureusement les entités (`E22 Human-Made Object`, `E73 Information Object`) et réifie les actes de représentation (`E13 Attribute Assignment`, propriété `P138 represents`)
- **FRBR / FRBRoo** — Modèle bibliothéconomique distinguant Œuvre / Expression / Manifestation / Item, où une même création intellectuelle existe simultanément à plusieurs niveaux

**Linguistique computationnelle** :

- **Frame Semantics** (Fillmore) — Structures de traits typés où chaque attribut peut être soit atomique soit une structure imbriquée
- **Typed Feature Structures** — Formalisme dans lequel la récursion est native

Le modèle de Th3Sr1b3Pr0j3ct ne prétend pas réinventer ces approches. Il vise à offrir une **infrastructure légère et accessible** qui en respecte les principes essentiels, sans la lourdeur de CIDOC-CRM ni la complexité de FRBR — adaptée aux besoins industriels de l'ingénierie des connaissances.

---

**Fin du document**
