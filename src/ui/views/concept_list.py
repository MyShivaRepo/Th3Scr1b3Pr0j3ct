"""Vue — Liste et recherche des entités conceptuelles."""

from __future__ import annotations

import streamlit as st

from src.model.concept import Concept, ConceptStatus
from src.model.identity import short_id


def render_concept_list(concepts: list[Concept]) -> str | None:
    """Affiche la liste filtrée des entités. Retourne l'URI sélectionnée ou None."""
    st.subheader("Référentiel d'entités")

    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Rechercher", placeholder="Filtrer par label…", key="search_text")
    with col2:
        status_options = ["Tous"] + [ConceptStatus.label(s) for s in ConceptStatus]
        status_filter = st.selectbox("Statut", status_options, key="status_filter")

    # Application des filtres
    filtered = concepts
    if search:
        search_lower = search.lower()
        filtered = [
            c for c in filtered
            if any(search_lower in lbl.lower() for lbl in c.all_labels())
        ]
    if status_filter != "Tous":
        target_status = next(
            s for s in ConceptStatus if ConceptStatus.label(s) == status_filter
        )
        filtered = [c for c in filtered if c.status == target_status]

    st.caption(f"{len(filtered)} entité(s) affichée(s) sur {len(concepts)}")

    if not filtered:
        st.info("Aucune entité ne correspond aux critères de recherche.")
        return None

    # En-tête tableau
    header = st.columns([3, 1, 1, 2])
    header[0].markdown("**Label préféré**")
    header[1].markdown("**ID court**")
    header[2].markdown("**Statut**")
    header[3].markdown("**Modifié le**")
    st.divider()

    selected_uri = None
    for concept in filtered:
        cols = st.columns([3, 1, 1, 2])
        label = concept.pref_label("fr")
        sid = short_id(concept.uri)
        status_lbl = ConceptStatus.label(concept.status)
        modified = concept.modified_at[:10] if concept.modified_at else "—"

        cols[0].write(label)
        cols[1].code(sid, language=None)
        status_colors = {
            ":Active": "🟢",
            ":Provisional": "🟡",
            ":Deprecated": "🔴",
        }
        cols[2].write(f"{status_colors.get(concept.status.value, '')} {status_lbl}")
        cols[3].write(modified)

        if cols[0].button("Éditer", key=f"edit_{concept.uri}", use_container_width=False):
            selected_uri = concept.uri

    return selected_uri
