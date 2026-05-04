"""Vue — Création d'une nouvelle entité conceptuelle."""

from __future__ import annotations

import streamlit as st

from src.model.assertions import DefinitionAssertion, LabelAssertion, NoteAssertion
from src.model.concept import Concept, ConceptStatus
from src.model.identity import short_id


def render_concept_create() -> Concept | None:
    """Affiche le formulaire de création. Retourne le Concept créé ou None."""
    st.subheader("Nouvelle entité conceptuelle")

    concept = Concept.new()
    st.caption(f"Identifiant généré : `{concept.uri}`")

    with st.form("form_create"):
        st.markdown("##### Descriptions intrinsèques (couche 2.3.1)")

        pref_fr = st.text_input("Label préféré (français) *", key="pref_fr")
        pref_en = st.text_input("Label préféré (anglais)", key="pref_en")
        alt_labels_raw = st.text_input(
            "Labels alternatifs (séparés par ';')", key="alt_labels"
        )
        definition_fr = st.text_area("Définition (français)", key="def_fr", height=120)
        note_fr = st.text_area("Note (français)", key="note_fr", height=80)
        scope_note_fr = st.text_area("Note de portée — scopeNote (français)", key="scopenote_fr", height=80)

        st.markdown("##### Statut")
        status_labels = {ConceptStatus.label(s): s for s in ConceptStatus}
        chosen_status_label = st.selectbox(
            "Statut initial",
            list(status_labels.keys()),
            index=list(status_labels.keys()).index("Provisoire"),
            key="create_status",
        )

        submitted = st.form_submit_button("Créer l'entité", type="primary")

    if submitted:
        if not pref_fr.strip():
            st.error("Le label préféré en français est obligatoire.")
            return None

        concept.labels.append(LabelAssertion(value=pref_fr.strip(), lang="fr", preferred=True))
        if pref_en.strip():
            concept.labels.append(LabelAssertion(value=pref_en.strip(), lang="en", preferred=True))
        for alt in alt_labels_raw.split(";"):
            alt = alt.strip()
            if alt:
                concept.labels.append(LabelAssertion(value=alt, lang="fr", preferred=False))
        if definition_fr.strip():
            concept.definitions.append(DefinitionAssertion(value=definition_fr.strip(), lang="fr"))
        if note_fr.strip():
            concept.notes.append(NoteAssertion(value=note_fr.strip(), lang="fr", scope=False))
        if scope_note_fr.strip():
            concept.notes.append(NoteAssertion(value=scope_note_fr.strip(), lang="fr", scope=True))

        concept.status = status_labels[chosen_status_label]
        st.success(f"Entité « {pref_fr.strip()} » créée (ID : {short_id(concept.uri)}…)")
        return concept

    return None
