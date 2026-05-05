"""Vue — Liste et recherche des entités conceptuelles."""

from __future__ import annotations

import streamlit as st

from src.model.concept import Concept, ConceptStatus
from src.model.identity import short_id


def render_concept_list(concepts: list[Concept]) -> tuple[str | None, str | None]:
    """Affiche la liste filtrée des entités.

    Retourne (uri_à_éditer, uri_à_supprimer) — au plus une des deux est non-None.
    """
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

    n_filtered = len(filtered)
    n_total = len(concepts)
    count_label = f"({n_filtered})" if n_filtered == n_total else f"({n_filtered} / {n_total})"
    st.subheader(f"Référentiel d'entités {count_label}")

    if not filtered:
        st.info("Aucune entité ne correspond aux critères de recherche.")
        return None, None

    st.divider()

    edit_uri = None
    delete_uri = None
    for concept in filtered:
        cols = st.columns([1, 1, 3, 1, 1, 2])
        label = concept.pref_label("fr")
        sid = short_id(concept.uri)
        status_lbl = ConceptStatus.label(concept.status)
        modified = concept.modified_at[:10] if concept.modified_at else "—"

        if cols[0].button("Éditer", key=f"edit_{concept.uri}", use_container_width=True):
            edit_uri = concept.uri
        if cols[1].button("Supprimer", key=f"del_{concept.uri}", use_container_width=True):
            delete_uri = concept.uri
        cols[2].write(label)
        cols[3].code(sid, language=None)
        status_colors = {
            ":Active": "🟢",
            ":Provisional": "🟡",
            ":Deprecated": "🔴",
        }
        cols[4].write(f"{status_colors.get(concept.status.value, '')} {status_lbl}")
        cols[5].write(modified)

    return edit_uri, delete_uri
