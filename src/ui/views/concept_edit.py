"""Vue — Édition complète d'une entité conceptuelle."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

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
from src.model.identity import increment_version, short_id
from src.ui.views.representation_edit import render_representation_section


def render_concept_edit(concept: Concept, all_concepts: list[Concept]) -> bool:
    """Affiche le formulaire d'édition complet. Retourne True si des modifications ont été sauvegardées."""
    st.subheader(f"Édition : {concept.pref_label('fr')}")
    st.caption(f"URI : `{concept.uri}` — ID court : `{short_id(concept.uri)}`")

    saved = False

    # ---- Statut ----
    with st.expander("Statut", expanded=True):
        status_labels = {ConceptStatus.label(s): s for s in ConceptStatus}
        current_label = ConceptStatus.label(concept.status)
        chosen = st.selectbox(
            "Statut",
            list(status_labels.keys()),
            index=list(status_labels.keys()).index(current_label),
            key=f"status_{concept.uri}",
        )
        concept.status = status_labels[chosen]

    # ---- Labels ----
    with st.expander("Labels (prefLabel / altLabel)", expanded=True):
        saved |= _edit_labels(concept)

    # ---- Définitions ----
    with st.expander("Définitions (skos:definition)"):
        saved |= _edit_definitions(concept)

    # ---- Notes ----
    with st.expander("Notes (skos:note / skos:scopeNote)"):
        saved |= _edit_notes(concept)

    # ---- Relations ----
    with st.expander("Relations à d'autres entités (couche 2.3.2)"):
        saved |= _edit_relations(concept, all_concepts)

    # ---- Actes de représentation ----
    with st.expander("Actes de représentation (couche 2.3.3)"):
        repr_modified = render_representation_section(concept, all_concepts)
        saved |= repr_modified

    # ---- Mappings ----
    with st.expander("Mappings inter-référentiels (couche 2.3.4)"):
        saved |= _edit_mappings(concept)

    # ---- Bouton sauvegarde global ----
    st.divider()
    if st.button("💾 Sauvegarder les modifications", type="primary", key=f"save_{concept.uri}"):
        concept.uri = increment_version(concept.uri)
        concept.modified_at = datetime.now(timezone.utc).isoformat()
        st.success(f"Entité sauvegardée — nouvelle version : `{concept.uri}`")
        saved = True

    return saved


# ---------------------------------------------------------------------------
# Sections d'édition internes
# ---------------------------------------------------------------------------

def _edit_labels(concept: Concept) -> bool:
    modified = False
    indices_to_delete = []
    for i, lbl in enumerate(concept.labels):
        cols = st.columns([2, 1, 1, 1])
        new_val = cols[0].text_input("Valeur", value=lbl.value, key=f"lbl_val_{concept.uri}_{i}")
        new_lang = cols[1].text_input("Langue", value=lbl.lang, key=f"lbl_lang_{concept.uri}_{i}", max_chars=5)
        new_pref = cols[2].checkbox("Préféré", value=lbl.preferred, key=f"lbl_pref_{concept.uri}_{i}")
        if cols[3].button("✕", key=f"lbl_del_{concept.uri}_{i}"):
            indices_to_delete.append(i)
            modified = True
        if new_val != lbl.value or new_lang != lbl.lang or new_pref != lbl.preferred:
            lbl.value = new_val
            lbl.lang = new_lang
            lbl.preferred = new_pref
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.labels.pop(i)

    with st.form(f"form_add_label_{concept.uri}"):
        c1, c2, c3 = st.columns([3, 1, 1])
        new_lbl = c1.text_input("Nouveau label", key=f"new_lbl_{concept.uri}")
        new_lang = c2.text_input("Langue", value="fr", key=f"new_lang_{concept.uri}", max_chars=5)
        new_pref = c3.checkbox("Préféré", value=False, key=f"new_pref_{concept.uri}")
        if st.form_submit_button("Ajouter"):
            if new_lbl.strip():
                concept.labels.append(LabelAssertion(value=new_lbl.strip(), lang=new_lang, preferred=new_pref))
                modified = True
    return modified


def _edit_definitions(concept: Concept) -> bool:
    modified = False
    indices_to_delete = []
    for i, defn in enumerate(concept.definitions):
        cols = st.columns([4, 1, 1])
        new_val = cols[0].text_area("Texte", value=defn.value, key=f"def_val_{concept.uri}_{i}", height=100)
        new_lang = cols[1].text_input("Langue", value=defn.lang, key=f"def_lang_{concept.uri}_{i}", max_chars=5)
        if cols[2].button("✕", key=f"def_del_{concept.uri}_{i}"):
            indices_to_delete.append(i)
            modified = True
        if new_val != defn.value or new_lang != defn.lang:
            defn.value = new_val
            defn.lang = new_lang
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.definitions.pop(i)

    with st.form(f"form_add_def_{concept.uri}"):
        c1, c2 = st.columns([4, 1])
        new_def = c1.text_area("Nouvelle définition", key=f"new_def_{concept.uri}", height=80)
        new_lang = c2.text_input("Langue", value="fr", key=f"new_deflang_{concept.uri}", max_chars=5)
        if st.form_submit_button("Ajouter"):
            if new_def.strip():
                concept.definitions.append(DefinitionAssertion(value=new_def.strip(), lang=new_lang))
                modified = True
    return modified


def _edit_notes(concept: Concept) -> bool:
    modified = False
    indices_to_delete = []
    for i, note in enumerate(concept.notes):
        note_type = "scopeNote" if note.scope else "note"
        cols = st.columns([4, 1, 1, 1])
        new_val = cols[0].text_area(f"[{note_type}]", value=note.value, key=f"note_val_{concept.uri}_{i}", height=80)
        new_lang = cols[1].text_input("Langue", value=note.lang, key=f"note_lang_{concept.uri}_{i}", max_chars=5)
        new_scope = cols[2].checkbox("scopeNote", value=note.scope, key=f"note_scope_{concept.uri}_{i}")
        if cols[3].button("✕", key=f"note_del_{concept.uri}_{i}"):
            indices_to_delete.append(i)
            modified = True
        if new_val != note.value or new_lang != note.lang or new_scope != note.scope:
            note.value = new_val
            note.lang = new_lang
            note.scope = new_scope
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.notes.pop(i)

    with st.form(f"form_add_note_{concept.uri}"):
        c1, c2, c3 = st.columns([4, 1, 1])
        new_note = c1.text_area("Nouvelle note", key=f"new_note_{concept.uri}", height=60)
        new_lang = c2.text_input("Langue", value="fr", key=f"new_notelang_{concept.uri}", max_chars=5)
        new_scope = c3.checkbox("scopeNote", value=False, key=f"new_scope_{concept.uri}")
        if st.form_submit_button("Ajouter"):
            if new_note.strip():
                concept.notes.append(NoteAssertion(value=new_note.strip(), lang=new_lang, scope=new_scope))
                modified = True
    return modified


def _edit_relations(concept: Concept, all_concepts: list[Concept]) -> bool:
    modified = False
    other_concepts = [c for c in all_concepts if c.uri != concept.uri]
    target_map = {c.uri: c.pref_label("fr") for c in other_concepts}

    indices_to_delete = []
    for i, rel in enumerate(concept.relations):
        target_label = target_map.get(rel.target_uri, rel.target_uri[:30] + "…")
        cols = st.columns([2, 3, 1])
        cols[0].write(f"`{rel.relation_type.value}`")
        cols[1].write(f"→ {target_label}")
        if cols[2].button("✕", key=f"rel_del_{concept.uri}_{i}"):
            indices_to_delete.append(i)
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.relations.pop(i)

    if other_concepts:
        with st.form(f"form_add_rel_{concept.uri}"):
            type_options = {rt.value: rt for rt in RelationType}
            target_options = {
                f"{c.pref_label('fr')} [{short_id(c.uri)}…]": c.uri
                for c in other_concepts
            }
            c1, c2 = st.columns(2)
            chosen_type = c1.selectbox("Type de relation", list(type_options.keys()), key=f"rel_type_{concept.uri}")
            chosen_target = c2.selectbox("Entité cible", list(target_options.keys()), key=f"rel_target_{concept.uri}")
            if st.form_submit_button("Ajouter la relation"):
                concept.relations.append(
                    RelationAssertion(
                        relation_type=type_options[chosen_type],
                        target_uri=target_options[chosen_target],
                    )
                )
                modified = True
    else:
        st.caption("Créez au moins une autre entité pour ajouter des relations.")
    return modified


def _edit_mappings(concept: Concept) -> bool:
    modified = False
    indices_to_delete = []
    for i, mapping in enumerate(concept.mappings):
        cols = st.columns([2, 4, 1])
        cols[0].write(f"`{mapping.mapping_type.value}`")
        cols[1].write(mapping.target_uri)
        if cols[2].button("✕", key=f"map_del_{concept.uri}_{i}"):
            indices_to_delete.append(i)
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.mappings.pop(i)

    with st.form(f"form_add_mapping_{concept.uri}"):
        type_options = {mt.value: mt for mt in MappingType}
        c1, c2 = st.columns([1, 3])
        chosen_type = c1.selectbox("Type", list(type_options.keys()), key=f"map_type_{concept.uri}")
        target_uri = c2.text_input("URI cible", key=f"map_target_{concept.uri}")
        if st.form_submit_button("Ajouter le mapping"):
            if target_uri.strip():
                concept.mappings.append(
                    MappingAssertion(
                        mapping_type=type_options[chosen_type],
                        target_uri=target_uri.strip(),
                    )
                )
                modified = True
    return modified
