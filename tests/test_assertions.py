"""Tests unitaires — couche 2 : assertions."""

from src.model.assertions import (
    DefinitionAssertion,
    LabelAssertion,
    MappingAssertion,
    MappingType,
    NoteAssertion,
    RelationAssertion,
    RelationType,
)


def test_label_assertion_preferred():
    lbl = LabelAssertion(value="Ingénierie des connaissances", lang="fr", preferred=True)
    assert lbl.preferred is True
    assert lbl.lang == "fr"


def test_label_assertion_alternative():
    lbl = LabelAssertion(value="KE", lang="en", preferred=False)
    assert lbl.preferred is False


def test_definition_assertion():
    defn = DefinitionAssertion(value="Un cadre méthodologique.", lang="fr")
    assert defn.lang == "fr"


def test_note_scope_flag():
    note = NoteAssertion(value="Note simple", lang="fr", scope=False)
    scope = NoteAssertion(value="Note de portée", lang="fr", scope=True)
    assert note.scope is False
    assert scope.scope is True


def test_relation_types_cover_spec():
    expected = {
        RelationType.BROADER, RelationType.NARROWER, RelationType.RELATED,
        RelationType.PRECEDES, RelationType.IMPLIES,
        RelationType.IS_PART_OF, RelationType.HAS_PART,
    }
    assert expected.issubset(set(RelationType))


def test_relation_assertion():
    rel = RelationAssertion(
        relation_type=RelationType.BROADER,
        target_uri="urn:concept:scribe:AABB#v1",
    )
    assert "AABB" in rel.target_uri


def test_mapping_types_cover_spec():
    expected = {
        MappingType.EXACT_MATCH, MappingType.CLOSE_MATCH,
        MappingType.BROAD_MATCH, MappingType.NARROW_MATCH,
        MappingType.SAME_AS,
    }
    assert expected == set(MappingType)


def test_mapping_assertion_with_confidence():
    m = MappingAssertion(
        mapping_type=MappingType.EXACT_MATCH,
        target_uri="http://www.w3.org/2004/02/skos/core#Concept",
        confidence=0.95,
        mapped_by="Bernard Chabot",
        mapped_on="2026-05-04",
    )
    assert m.confidence == 0.95
    assert m.mapped_by == "Bernard Chabot"


def test_mapping_assertion_minimal():
    m = MappingAssertion(mapping_type=MappingType.SAME_AS, target_uri="http://example.org/X")
    assert m.confidence is None
    assert m.mapped_by is None
