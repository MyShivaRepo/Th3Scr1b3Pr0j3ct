"""Couche 2.3.3 — Actes de représentation : relation récursive sujet/objet."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RepresentationKind(str, Enum):
    """Types de représentation disponibles (section 2.3.3)."""
    PHYSICAL_SCALE_MODEL = ":PhysicalScaleModel"
    TECHNICAL_DRAWING = ":TechnicalDrawing"
    PHOTOGRAPH = ":Photograph"
    DIGITAL_IMAGE = ":DigitalImage"
    VIDEO = ":Video"
    AUDIO_RECORDING = ":AudioRecording"
    DOCUMENT = ":Document"
    WEB_RESOURCE = ":WebResource"
    DIAGRAM = ":Diagram"
    DIGITAL_TWIN_3D = ":DigitalTwin3D"
    EMBEDDING = ":Embedding"

    @classmethod
    def label(cls, kind: "RepresentationKind") -> str:
        """Retourne un libellé lisible pour l'interface."""
        _labels = {
            cls.PHYSICAL_SCALE_MODEL: "Maquette physique",
            cls.TECHNICAL_DRAWING: "Plan / schéma technique",
            cls.PHOTOGRAPH: "Photographie",
            cls.DIGITAL_IMAGE: "Image numérique",
            cls.VIDEO: "Vidéo",
            cls.AUDIO_RECORDING: "Enregistrement audio",
            cls.DOCUMENT: "Document texte",
            cls.WEB_RESOURCE: "Ressource web",
            cls.DIAGRAM: "Diagramme conceptuel",
            cls.DIGITAL_TWIN_3D: "Modèle 3D / jumeau numérique",
            cls.EMBEDDING: "Représentation vectorielle (itération 3)",
        }
        return _labels.get(kind, kind.value)


@dataclass
class RepresentationAct:
    """Acte de représentation reliant un sujet (entité source) à un objet (entité cible).

    Modélisé en RDF comme nœud blanc (blank node) sur la propriété :isRepresentedBy
    de l'entité source. La cible (objet) est elle-même une entité indépendante,
    ce qui permet la récursion non bornée (section 2.3.3).
    """
    target_uri: str                          # URI de l'entité cible (l'objet/la représentation)
    kind: RepresentationKind                 # :representationKind
    context: Optional[str] = None           # :representationContext
    created_by: Optional[str] = None        # :representationCreatedBy
    created_on: Optional[str] = None        # :representationCreatedOn (date ISO 8601)
