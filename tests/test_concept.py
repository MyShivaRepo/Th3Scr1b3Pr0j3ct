"""Tests unitaires — modèle Concept."""

from src.model.assertions import DefinitionAssertion, LabelAssertion, RelationAssertion, RelationType
from src.model.concept import Concept, ConceptStatus
from src.model.identity import extract_version, is_valid_uri


def test_concept_new_has_valid_uri():
    c = Concept.new()
    assert is_valid_uri(c.uri)


def test_concept_new_initial_version():
    c = Concept.new()
    assert extract_version(c.uri) == 1


def test_concept_new_provisional_status():
    c = Concept.new()
    assert c.status == ConceptStatus.PROVISIONAL


def test_concept_pref_label_fr():
    c = Concept.new()
    c.labels.append(LabelAssertion(value="Ingénierie des connaissances", lang="fr", preferred=True))
    c.labels.append(LabelAssertion(value="Knowledge Engineering", lang="en", preferred=True))
    assert c.pref_label("fr") == "Ingénierie des connaissances"
    assert c.pref_label("en") == "Knowledge Engineering"


def test_concept_pref_label_fallback():
    c = Concept.new()
    c.labels.append(LabelAssertion(value="KE", lang="en", preferred=True))
    # Pas de label FR — doit retourner l'EN
    assert c.pref_label("fr") == "KE"


def test_concept_pref_label_no_label():
    c = Concept.new()
    assert c.pref_label() == "(sans label)"


def test_concept_all_labels():
    c = Concept.new()
    c.labels.append(LabelAssertion(value="KRVF", lang="fr", preferred=True))
    c.labels.append(LabelAssertion(value="Knowledge Representation", lang="en", preferred=True))
    c.labels.append(LabelAssertion(value="KR", lang="en", preferred=False))
    all_lbls = c.all_labels()
    assert "KRVF" in all_lbls
    assert "KR" in all_lbls
    assert len(all_lbls) == 3


def test_concept_uuid_immutable_after_add_label():
    c = Concept.new()
    original_base = c.uri.split("#")[0]
    c.labels.append(LabelAssertion(value="Test", lang="fr", preferred=True))
    assert c.uri.split("#")[0] == original_base


def test_concept_status_change():
    c = Concept.new()
    assert c.status == ConceptStatus.PROVISIONAL
    c.status = ConceptStatus.ACTIVE
    assert c.status == ConceptStatus.ACTIVE


def test_concept_status_labels():
    assert ConceptStatus.label(ConceptStatus.ACTIVE) == "Actif"
    assert ConceptStatus.label(ConceptStatus.PROVISIONAL) == "Provisoire"
    assert ConceptStatus.label(ConceptStatus.DEPRECATED) == "Déprécié"
