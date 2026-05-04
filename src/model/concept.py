"""Modèle d'entité conceptuelle — articulation des couches 1, 2 et 3 (statut)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from src.model.assertions import (
    LabelAssertion,
    DefinitionAssertion,
    NoteAssertion,
    RelationAssertion,
    MappingAssertion,
)
from src.model.identity import generate_uri
from src.model.representation import RepresentationAct


class ConceptStatus(str, Enum):
    """Statuts d'une entité conceptuelle (couche 3 partielle — section 2.4)."""
    ACTIVE = ":Active"
    PROVISIONAL = ":Provisional"
    DEPRECATED = ":Deprecated"

    @classmethod
    def label(cls, status: "ConceptStatus") -> str:
        """Retourne un libellé lisible pour l'interface."""
        return {
            cls.ACTIVE: "Actif",
            cls.PROVISIONAL: "Provisoire",
            cls.DEPRECATED: "Déprécié",
        }[status]


@dataclass
class Concept:
    """Entité conceptuelle du référentiel Th3Sr1b3Pr0j3ct.

    Chaque instance possède un URI opaque et persistant (couche 1) et une
    collection d'assertions (couche 2) qui construisent progressivement son sens.
    """
    uri: str                                             # Couche 1 — identifiant versionné
    status: ConceptStatus = ConceptStatus.PROVISIONAL
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Couche 2.3.1 — Descriptions intrinsèques
    labels: list[LabelAssertion] = field(default_factory=list)
    definitions: list[DefinitionAssertion] = field(default_factory=list)
    notes: list[NoteAssertion] = field(default_factory=list)

    # Couche 2.3.2 — Relations
    relations: list[RelationAssertion] = field(default_factory=list)

    # Couche 2.3.3 — Actes de représentation (sortants : self est le sujet)
    representations_out: list[RepresentationAct] = field(default_factory=list)

    # Couche 2.3.4 — Mappings inter-référentiels
    mappings: list[MappingAssertion] = field(default_factory=list)

    @classmethod
    def new(cls) -> "Concept":
        """Crée une nouvelle entité avec URI généré, statut Provisional."""
        return cls(uri=generate_uri())

    def pref_label(self, lang: str = "fr") -> str:
        """Retourne le label préféré dans la langue demandée, ou dans n'importe quelle langue."""
        for lbl in self.labels:
            if lbl.preferred and lbl.lang == lang:
                return lbl.value
        for lbl in self.labels:
            if lbl.preferred:
                return lbl.value
        return "(sans label)"

    def all_labels(self) -> list[str]:
        """Retourne tous les labels (toutes langues, préférés et alternatifs)."""
        return [lbl.value for lbl in self.labels]
