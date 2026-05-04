"""Couche 2 — Assertions : tous les types de contributions au sens d'une entité."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# 2.3.1 — Descriptions intrinsèques
# ---------------------------------------------------------------------------

@dataclass
class LabelAssertion:
    """Libellé associé à une langue (prefLabel ou altLabel)."""
    value: str
    lang: str
    preferred: bool = True  # True = skos:prefLabel, False = skos:altLabel


@dataclass
class DefinitionAssertion:
    """Définition textuelle en langue donnée (skos:definition)."""
    value: str
    lang: str


@dataclass
class NoteAssertion:
    """Note textuelle (skos:note ou skos:scopeNote)."""
    value: str
    lang: str
    scope: bool = False  # True = skos:scopeNote, False = skos:note


# ---------------------------------------------------------------------------
# 2.3.2 — Relations à d'autres entités
# ---------------------------------------------------------------------------

class RelationType(str, Enum):
    """Types de relations sémantiques entre entités (section 2.3.2)."""
    BROADER = "skos:broader"
    NARROWER = "skos:narrower"
    RELATED = "skos:related"
    PRECEDES = ":precedes"
    IMPLIES = ":implies"
    IS_PART_OF = ":isPartOf"
    HAS_PART = ":hasPart"
    # Relations custom du référentiel Bernard Chabot
    IS_EXTENSION_OF = ":isExtensionOf"
    ARTICULATES_WITH = ":articulatesWith"
    USES_TECHNOLOGY = ":usesTechnology"
    IS_FRAMEWORK_FOR = ":isFrameworkFor"
    IS_BUILT_UPON = ":isBuiltUpon"
    EXTENDS_TECHNOLOGY = ":extendsTechnology"


@dataclass
class RelationAssertion:
    """Assertion de relation entre deux entités (section 2.3.2)."""
    relation_type: RelationType
    target_uri: str  # URI de l'entité cible


# ---------------------------------------------------------------------------
# 2.3.4 — Mappings inter-référentiels
# ---------------------------------------------------------------------------

class MappingType(str, Enum):
    """Types de mappings vers des référentiels externes (section 2.3.4)."""
    EXACT_MATCH = "skos:exactMatch"
    CLOSE_MATCH = "skos:closeMatch"
    BROAD_MATCH = "skos:broadMatch"
    NARROW_MATCH = "skos:narrowMatch"
    SAME_AS = "owl:sameAs"


@dataclass
class MappingAssertion:
    """Assertion de mapping vers un référentiel externe (section 2.3.4)."""
    mapping_type: MappingType
    target_uri: str
    confidence: Optional[float] = None   # :hasConfidence — entre 0.0 et 1.0
    mapped_by: Optional[str] = None      # :wasMappedBy
    mapped_on: Optional[str] = None      # :wasMappedOn (date ISO 8601)
