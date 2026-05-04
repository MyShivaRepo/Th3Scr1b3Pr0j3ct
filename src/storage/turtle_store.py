"""Couche stockage — sérialisation / désérialisation RDF Turtle via rdflib."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

from src.model.assertions import (
    DefinitionAssertion,
    LabelAssertion,
    MappingAssertion,
    MappingType,
    NoteAssertion,
    RelationAssertion,
    RelationType,
)
from src.model.concept import Concept, ConceptStatus
from src.model.identity import base_uri, extract_version, increment_version
from src.model.representation import RepresentationAct, RepresentationKind

# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------
SCRIBE = Namespace("urn:scribe:vocabulary#")
CONCEPT_NS = Namespace("urn:concept:scribe:")

_RELATION_TYPE_MAP: dict[RelationType, URIRef] = {
    RelationType.BROADER: SKOS.broader,
    RelationType.NARROWER: SKOS.narrower,
    RelationType.RELATED: SKOS.related,
    RelationType.PRECEDES: SCRIBE.precedes,
    RelationType.IMPLIES: SCRIBE.implies,
    RelationType.IS_PART_OF: SCRIBE.isPartOf,
    RelationType.HAS_PART: SCRIBE.hasPart,
    RelationType.IS_EXTENSION_OF: SCRIBE.isExtensionOf,
    RelationType.ARTICULATES_WITH: SCRIBE.articulatesWith,
    RelationType.USES_TECHNOLOGY: SCRIBE.usesTechnology,
    RelationType.IS_FRAMEWORK_FOR: SCRIBE.isFrameworkFor,
    RelationType.IS_BUILT_UPON: SCRIBE.isBuiltUpon,
    RelationType.EXTENDS_TECHNOLOGY: SCRIBE.extendsTechnology,
}

_MAPPING_TYPE_MAP: dict[MappingType, URIRef] = {
    MappingType.EXACT_MATCH: SKOS.exactMatch,
    MappingType.CLOSE_MATCH: SKOS.closeMatch,
    MappingType.BROAD_MATCH: SKOS.broadMatch,
    MappingType.NARROW_MATCH: SKOS.narrowMatch,
    MappingType.SAME_AS: OWL.sameAs,
}

_STATUS_MAP: dict[ConceptStatus, URIRef] = {
    ConceptStatus.ACTIVE: SCRIBE.Active,
    ConceptStatus.PROVISIONAL: SCRIBE.Provisional,
    ConceptStatus.DEPRECATED: SCRIBE.Deprecated,
}

_STATUS_REVERSE: dict[str, ConceptStatus] = {
    str(SCRIBE.Active): ConceptStatus.ACTIVE,
    str(SCRIBE.Provisional): ConceptStatus.PROVISIONAL,
    str(SCRIBE.Deprecated): ConceptStatus.DEPRECATED,
}

_REPR_KIND_MAP: dict[RepresentationKind, URIRef] = {
    RepresentationKind.PHYSICAL_SCALE_MODEL: SCRIBE.PhysicalScaleModel,
    RepresentationKind.TECHNICAL_DRAWING: SCRIBE.TechnicalDrawing,
    RepresentationKind.PHOTOGRAPH: SCRIBE.Photograph,
    RepresentationKind.DIGITAL_IMAGE: SCRIBE.DigitalImage,
    RepresentationKind.VIDEO: SCRIBE.Video,
    RepresentationKind.AUDIO_RECORDING: SCRIBE.AudioRecording,
    RepresentationKind.DOCUMENT: SCRIBE.Document,
    RepresentationKind.WEB_RESOURCE: SCRIBE.WebResource,
    RepresentationKind.DIAGRAM: SCRIBE.Diagram,
    RepresentationKind.DIGITAL_TWIN_3D: SCRIBE.DigitalTwin3D,
    RepresentationKind.EMBEDDING: SCRIBE.Embedding,
}

_REPR_KIND_REVERSE: dict[str, RepresentationKind] = {
    str(v): k for k, v in _REPR_KIND_MAP.items()
}

_RELATION_REVERSE: dict[str, RelationType] = {
    str(v): k for k, v in _RELATION_TYPE_MAP.items()
}

_MAPPING_REVERSE: dict[str, MappingType] = {
    str(v): k for k, v in _MAPPING_TYPE_MAP.items()
}


def _uri_ref(uri: str) -> URIRef:
    return URIRef(uri)


# ---------------------------------------------------------------------------
# Sérialisation
# ---------------------------------------------------------------------------

def _concept_to_graph(concept: Concept, g: Graph) -> None:
    """Ajoute toutes les triplets d'un concept dans le graphe RDF."""
    subj = _uri_ref(concept.uri)

    g.add((subj, RDF.type, SCRIBE.Concept))
    g.add((subj, SCRIBE.hasStatus, _STATUS_MAP[concept.status]))
    g.add((subj, SCRIBE.createdAt, Literal(concept.created_at, datatype=XSD.dateTime)))
    g.add((subj, SCRIBE.modifiedAt, Literal(concept.modified_at, datatype=XSD.dateTime)))

    # Couche 2.3.1 — Labels et descriptions
    for lbl in concept.labels:
        pred = SKOS.prefLabel if lbl.preferred else SKOS.altLabel
        g.add((subj, pred, Literal(lbl.value, lang=lbl.lang)))

    for defn in concept.definitions:
        g.add((subj, SKOS.definition, Literal(defn.value, lang=defn.lang)))

    for note in concept.notes:
        pred = SKOS.scopeNote if note.scope else SKOS.note
        g.add((subj, pred, Literal(note.value, lang=note.lang)))

    # Couche 2.3.2 — Relations
    for rel in concept.relations:
        pred = _RELATION_TYPE_MAP[rel.relation_type]
        g.add((subj, pred, _uri_ref(rel.target_uri)))

    # Couche 2.3.3 — Actes de représentation (nœuds blancs)
    for act in concept.representations_out:
        bn = BNode()
        g.add((subj, SCRIBE.isRepresentedBy, bn))
        g.add((bn, SCRIBE.representation, _uri_ref(act.target_uri)))
        g.add((bn, SCRIBE.representationKind, _REPR_KIND_MAP[act.kind]))
        if act.context:
            g.add((bn, SCRIBE.representationContext, Literal(act.context, lang="fr")))
        if act.created_by:
            g.add((bn, SCRIBE.representationCreatedBy, Literal(act.created_by)))
        if act.created_on:
            g.add((bn, SCRIBE.representationCreatedOn,
                   Literal(act.created_on, datatype=XSD.date)))

    # Couche 2.3.4 — Mappings
    for mapping in concept.mappings:
        pred = _MAPPING_TYPE_MAP[mapping.mapping_type]
        target = _uri_ref(mapping.target_uri)
        if mapping.confidence is not None or mapping.mapped_by or mapping.mapped_on:
            bn = BNode()
            g.add((subj, SCRIBE.hasMapping, bn))
            g.add((bn, SCRIBE.mappingType, pred))
            g.add((bn, SCRIBE.mappingTarget, target))
            if mapping.confidence is not None:
                g.add((bn, SCRIBE.hasConfidence,
                       Literal(mapping.confidence, datatype=XSD.decimal)))
            if mapping.mapped_by:
                g.add((bn, SCRIBE.wasMappedBy, Literal(mapping.mapped_by)))
            if mapping.mapped_on:
                g.add((bn, SCRIBE.wasMappedOn,
                       Literal(mapping.mapped_on, datatype=XSD.date)))
        else:
            g.add((subj, pred, target))


# ---------------------------------------------------------------------------
# Désérialisation
# ---------------------------------------------------------------------------

def _graph_to_concept(subj: URIRef, g: Graph) -> Concept:
    """Reconstruit un Concept depuis les triplets RDF d'un sujet."""
    uri = str(subj)

    # Statut
    status_uris = list(g.objects(subj, SCRIBE.hasStatus))
    status = _STATUS_REVERSE.get(str(status_uris[0]), ConceptStatus.PROVISIONAL) if status_uris else ConceptStatus.PROVISIONAL

    # Timestamps
    created_at_vals = list(g.objects(subj, SCRIBE.createdAt))
    modified_at_vals = list(g.objects(subj, SCRIBE.modifiedAt))
    created_at = str(created_at_vals[0]) if created_at_vals else ""
    modified_at = str(modified_at_vals[0]) if modified_at_vals else ""

    # Labels
    labels: list[LabelAssertion] = []
    for obj in g.objects(subj, SKOS.prefLabel):
        labels.append(LabelAssertion(value=str(obj), lang=obj.language or "fr", preferred=True))
    for obj in g.objects(subj, SKOS.altLabel):
        labels.append(LabelAssertion(value=str(obj), lang=obj.language or "fr", preferred=False))

    # Définitions
    definitions: list[DefinitionAssertion] = []
    for obj in g.objects(subj, SKOS.definition):
        definitions.append(DefinitionAssertion(value=str(obj), lang=obj.language or "fr"))

    # Notes
    notes: list[NoteAssertion] = []
    for obj in g.objects(subj, SKOS.note):
        notes.append(NoteAssertion(value=str(obj), lang=obj.language or "fr", scope=False))
    for obj in g.objects(subj, SKOS.scopeNote):
        notes.append(NoteAssertion(value=str(obj), lang=obj.language or "fr", scope=True))

    # Relations
    relations: list[RelationAssertion] = []
    for pred, obj in g.predicate_objects(subj):
        rel_type = _RELATION_REVERSE.get(str(pred))
        if rel_type and isinstance(obj, URIRef):
            relations.append(RelationAssertion(relation_type=rel_type, target_uri=str(obj)))

    # Actes de représentation
    representations_out: list[RepresentationAct] = []
    for bn in g.objects(subj, SCRIBE.isRepresentedBy):
        target_list = list(g.objects(bn, SCRIBE.representation))
        kind_list = list(g.objects(bn, SCRIBE.representationKind))
        if not target_list or not kind_list:
            continue
        target_uri = str(target_list[0])
        kind = _REPR_KIND_REVERSE.get(str(kind_list[0]), RepresentationKind.DOCUMENT)
        context_list = list(g.objects(bn, SCRIBE.representationContext))
        created_by_list = list(g.objects(bn, SCRIBE.representationCreatedBy))
        created_on_list = list(g.objects(bn, SCRIBE.representationCreatedOn))
        representations_out.append(RepresentationAct(
            target_uri=target_uri,
            kind=kind,
            context=str(context_list[0]) if context_list else None,
            created_by=str(created_by_list[0]) if created_by_list else None,
            created_on=str(created_on_list[0]) if created_on_list else None,
        ))

    # Mappings
    mappings: list[MappingAssertion] = []
    for bn in g.objects(subj, SCRIBE.hasMapping):
        mtype_list = list(g.objects(bn, SCRIBE.mappingType))
        mtarget_list = list(g.objects(bn, SCRIBE.mappingTarget))
        if not mtype_list or not mtarget_list:
            continue
        mtype = _MAPPING_REVERSE.get(str(mtype_list[0]))
        if not mtype:
            continue
        conf_list = list(g.objects(bn, SCRIBE.hasConfidence))
        by_list = list(g.objects(bn, SCRIBE.wasMappedBy))
        on_list = list(g.objects(bn, SCRIBE.wasMappedOn))
        mappings.append(MappingAssertion(
            mapping_type=mtype,
            target_uri=str(mtarget_list[0]),
            confidence=float(conf_list[0]) if conf_list else None,
            mapped_by=str(by_list[0]) if by_list else None,
            mapped_on=str(on_list[0]) if on_list else None,
        ))
    # Mappings simples (sans nœud blanc)
    for pred, obj in g.predicate_objects(subj):
        mtype = _MAPPING_REVERSE.get(str(pred))
        if mtype and isinstance(obj, URIRef):
            mappings.append(MappingAssertion(mapping_type=mtype, target_uri=str(obj)))

    return Concept(
        uri=uri,
        status=status,
        created_at=created_at,
        modified_at=modified_at,
        labels=labels,
        definitions=definitions,
        notes=notes,
        relations=relations,
        representations_out=representations_out,
        mappings=mappings,
    )


# ---------------------------------------------------------------------------
# Interface publique
# ---------------------------------------------------------------------------

class TurtleStore:
    """Gestionnaire de persistance RDF Turtle pour le référentiel."""

    def __init__(self, path: str | Path) -> None:
        """Initialise le store avec le chemin du fichier .ttl principal."""
        self.path = Path(path)

    def _build_graph(self, concepts: list[Concept]) -> Graph:
        g = Graph()
        g.bind("skos", SKOS)
        g.bind("owl", OWL)
        g.bind("xsd", XSD)
        g.bind("scribe", SCRIBE)
        for concept in concepts:
            _concept_to_graph(concept, g)
        return g

    def save(self, concepts: list[Concept]) -> None:
        """Sérialise la liste de concepts dans le fichier Turtle."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        g = self._build_graph(concepts)
        g.serialize(destination=str(self.path), format="turtle")

    def load(self) -> list[Concept]:
        """Désérialise tous les concepts depuis le fichier Turtle."""
        if not self.path.exists():
            return []
        g = Graph()
        g.parse(str(self.path), format="turtle")
        concepts = []
        for subj in g.subjects(RDF.type, SCRIBE.Concept):
            if isinstance(subj, URIRef):
                concepts.append(_graph_to_concept(subj, g))
        return concepts

    def load_from_file(self, seed_path: str | Path) -> list[Concept]:
        """Charge des concepts depuis un fichier Turtle externe (seed)."""
        g = Graph()
        g.parse(str(seed_path), format="turtle")
        concepts = []
        for subj in g.subjects(RDF.type, SCRIBE.Concept):
            if isinstance(subj, URIRef):
                concepts.append(_graph_to_concept(subj, g))
        return concepts
