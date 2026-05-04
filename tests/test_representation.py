"""Tests unitaires — couche 2.3.3 : actes de représentation."""

import pytest

from src.model.representation import RepresentationAct, RepresentationKind


def test_representation_kind_values():
    """Tous les types de la spec doivent être présents."""
    spec_kinds = {
        ":PhysicalScaleModel", ":TechnicalDrawing", ":Photograph",
        ":DigitalImage", ":Video", ":AudioRecording", ":Document",
        ":WebResource", ":Diagram", ":DigitalTwin3D", ":Embedding",
    }
    actual = {k.value for k in RepresentationKind}
    assert spec_kinds == actual


def test_representation_act_minimal():
    act = RepresentationAct(
        target_uri="urn:concept:scribe:AABB#v1",
        kind=RepresentationKind.DOCUMENT,
    )
    assert act.context is None
    assert act.created_by is None
    assert act.created_on is None


def test_representation_act_full():
    act = RepresentationAct(
        target_uri="urn:concept:scribe:AABB#v1",
        kind=RepresentationKind.DIAGRAM,
        context="Présentation portes ouvertes",
        created_by="Bernard Chabot",
        created_on="2026-05-04",
    )
    assert act.context == "Présentation portes ouvertes"
    assert act.created_by == "Bernard Chabot"
    assert act.created_on == "2026-05-04"


def test_representation_kind_label():
    assert "Maquette" in RepresentationKind.label(RepresentationKind.PHYSICAL_SCALE_MODEL)
    assert "Diagramme" in RepresentationKind.label(RepresentationKind.DIAGRAM)
    assert "Document" in RepresentationKind.label(RepresentationKind.DOCUMENT)


def test_recursion_chain():
    """Vérifie qu'une chaîne de représentations A→B→C→D est constructible."""
    uri_a = "urn:concept:scribe:AAAA#v1"
    uri_b = "urn:concept:scribe:BBBB#v1"
    uri_c = "urn:concept:scribe:CCCC#v1"
    uri_d = "urn:concept:scribe:DDDD#v1"

    act_a = RepresentationAct(target_uri=uri_b, kind=RepresentationKind.DIAGRAM)
    act_b = RepresentationAct(target_uri=uri_c, kind=RepresentationKind.PHOTOGRAPH)
    act_c = RepresentationAct(target_uri=uri_d, kind=RepresentationKind.DIGITAL_IMAGE)

    # La chaîne est simplement une liste de RepresentationAct sur des entités différentes
    assert act_a.target_uri == uri_b
    assert act_b.target_uri == uri_c
    assert act_c.target_uri == uri_d
