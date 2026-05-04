"""Tests unitaires — couche stockage : TurtleStore."""

import tempfile
from pathlib import Path

import pytest

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
from src.model.representation import RepresentationAct, RepresentationKind
from src.storage.turtle_store import TurtleStore


def _make_store(tmp_path: Path) -> TurtleStore:
    return TurtleStore(tmp_path / "test_concepts.ttl")


def _sample_concept(pref_label: str = "Test") -> Concept:
    c = Concept.new()
    c.status = ConceptStatus.ACTIVE
    c.labels.append(LabelAssertion(value=pref_label, lang="fr", preferred=True))
    c.labels.append(LabelAssertion(value=f"{pref_label} EN", lang="en", preferred=True))
    c.labels.append(LabelAssertion(value=f"{pref_label}-alt", lang="fr", preferred=False))
    c.definitions.append(DefinitionAssertion(value="Une définition.", lang="fr"))
    c.notes.append(NoteAssertion(value="Une note.", lang="fr", scope=False))
    c.notes.append(NoteAssertion(value="Note de portée.", lang="fr", scope=True))
    return c


def test_save_and_load_empty(tmp_path):
    store = _make_store(tmp_path)
    store.save([])
    result = store.load()
    assert result == []


def test_save_and_load_single_concept(tmp_path):
    store = _make_store(tmp_path)
    c = _sample_concept("KRVF")
    store.save([c])
    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0].uri == c.uri
    assert loaded[0].pref_label("fr") == "KRVF"


def test_uuid_preserved_after_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    c = _sample_concept()
    original_uri = c.uri
    store.save([c])
    loaded = store.load()
    assert loaded[0].uri == original_uri


def test_status_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    c = _sample_concept()
    c.status = ConceptStatus.DEPRECATED
    store.save([c])
    loaded = store.load()
    assert loaded[0].status == ConceptStatus.DEPRECATED


def test_all_labels_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    c = _sample_concept("PLM")
    store.save([c])
    loaded = store.load()
    labels = loaded[0].all_labels()
    assert "PLM" in labels
    assert "PLM EN" in labels
    assert "PLM-alt" in labels


def test_definition_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    c = _sample_concept()
    store.save([c])
    loaded = store.load()
    assert any(d.value == "Une définition." for d in loaded[0].definitions)


def test_notes_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    c = _sample_concept()
    store.save([c])
    loaded = store.load()
    assert any(n.scope is False and n.value == "Une note." for n in loaded[0].notes)
    assert any(n.scope is True for n in loaded[0].notes)


def test_relation_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    c1 = _sample_concept("A")
    c2 = _sample_concept("B")
    c1.relations.append(RelationAssertion(relation_type=RelationType.BROADER, target_uri=c2.uri))
    store.save([c1, c2])
    loaded = store.load()
    c1_loaded = next(c for c in loaded if c.uri == c1.uri)
    assert len(c1_loaded.relations) == 1
    assert c1_loaded.relations[0].relation_type == RelationType.BROADER
    assert c1_loaded.relations[0].target_uri == c2.uri


def test_representation_act_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    c1 = _sample_concept("Sujet")
    c2 = _sample_concept("Objet")
    c1.representations_out.append(
        RepresentationAct(
            target_uri=c2.uri,
            kind=RepresentationKind.DOCUMENT,
            context="Contexte test",
            created_by="Bernard Chabot",
            created_on="2026-05-04",
        )
    )
    store.save([c1, c2])
    loaded = store.load()
    c1_loaded = next(c for c in loaded if c.uri == c1.uri)
    assert len(c1_loaded.representations_out) == 1
    act = c1_loaded.representations_out[0]
    assert act.target_uri == c2.uri
    assert act.kind == RepresentationKind.DOCUMENT
    assert act.created_by == "Bernard Chabot"


def test_load_returns_empty_when_file_absent(tmp_path):
    store = TurtleStore(tmp_path / "nonexistent.ttl")
    assert store.load() == []


def test_multiple_concepts_roundtrip(tmp_path):
    store = _make_store(tmp_path)
    concepts = [_sample_concept(f"Concept {i}") for i in range(5)]
    store.save(concepts)
    loaded = store.load()
    assert len(loaded) == 5
    uris_saved = {c.uri for c in concepts}
    uris_loaded = {c.uri for c in loaded}
    assert uris_saved == uris_loaded


def test_seed_file_loads(tmp_path):
    """Vérifie que le fichier seed se charge sans erreur."""
    seed_path = Path(__file__).parent.parent / "data" / "seed" / "bernard_concepts.ttl"
    if not seed_path.exists():
        pytest.skip("Fichier seed absent")
    store = _make_store(tmp_path)
    concepts = store.load_from_file(seed_path)
    assert len(concepts) == 12
