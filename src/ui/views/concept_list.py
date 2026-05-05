"""Vue — Liste et recherche des entités conceptuelles."""

from __future__ import annotations

import streamlit as st

from src.model.concept import Concept, ConceptStatus
from src.model.identity import short_id

# Colonnes triables : clé interne → (label affiché, fonction de tri)
_SORT_COLUMNS: dict[str, tuple[str, callable]] = {
    "label":    ("Label (fr)",   lambda c: c.pref_label("fr").lower()),
    "id":       ("ID court",     lambda c: short_id(c.uri).lower()),
    "status":   ("Statut",       lambda c: c.status.value),
    "modified": ("Modifié le",   lambda c: c.modified_at or ""),
}


def _sort_icon(col_key: str) -> str:
    """Retourne l'icône de tri pour un en-tête de colonne."""
    if st.session_state.get("sort_col") != col_key:
        return " ⇅"
    return " ▲" if st.session_state.get("sort_asc", True) else " ▼"


def _on_sort_click(col_key: str) -> None:
    """Bascule le tri sur la colonne cliquée."""
    if st.session_state.get("sort_col") == col_key:
        st.session_state["sort_asc"] = not st.session_state.get("sort_asc", True)
    else:
        st.session_state["sort_col"] = col_key
        st.session_state["sort_asc"] = True


def render_concept_list(concepts: list[Concept]) -> tuple[str | None, str | None, bool]:
    """Affiche la liste filtrée et triable des entités.

    Retourne (uri_à_éditer, uri_à_supprimer, ajouter_cliqué).
    """
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Rechercher", placeholder="Filtrer par label…", key="search_text")
    with col2:
        status_options = ["Tous"] + [ConceptStatus.label(s) for s in ConceptStatus]
        status_filter = st.selectbox("Statut", status_options, key="status_filter")

    # Filtrage
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

    # Tri
    sort_col = st.session_state.get("sort_col", "label")
    sort_asc = st.session_state.get("sort_asc", True)
    sort_fn = _SORT_COLUMNS.get(sort_col, _SORT_COLUMNS["label"])[1]
    filtered = sorted(filtered, key=sort_fn, reverse=not sort_asc)

    n_filtered = len(filtered)
    n_total = len(concepts)
    count_label = f"({n_filtered})" if n_filtered == n_total else f"({n_filtered} / {n_total})"

    title_col, btn_col = st.columns([5, 1])
    title_col.subheader(f"Référentiel d'entités {count_label}")
    add_clicked = btn_col.button("➕ Ajouter", use_container_width=True)

    if not filtered:
        st.info("Aucune entité ne correspond aux critères de recherche.")
        return None, None, add_clicked

    st.divider()

    # En-têtes cliquables — layout : [Éditer, Supprimer, Label, Définition, ID, Statut, Modifié]
    h = st.columns([1, 1, 3, 4, 1, 1, 2])
    for col_key, (col_label, _) in _SORT_COLUMNS.items():
        idx = {"label": 2, "id": 4, "status": 5, "modified": 6}[col_key]
        if h[idx].button(
            col_label + _sort_icon(col_key),
            key=f"sort_{col_key}",
            use_container_width=True,
        ):
            _on_sort_click(col_key)
            st.rerun()
    h[3].markdown("**Définition (fr)**")
    st.divider()

    edit_uri = None
    delete_uri = None
    for concept in filtered:
        cols = st.columns([1, 1, 3, 4, 1, 1, 2])
        label = concept.pref_label("fr")
        definition = next((d.value for d in concept.definitions if d.lang == "fr"), "")
        definition_short = definition[:120] + "…" if len(definition) > 120 else definition
        sid = short_id(concept.uri)
        status_lbl = ConceptStatus.label(concept.status)
        modified = concept.modified_at[:10] if concept.modified_at else "—"

        if cols[0].button("Éditer", key=f"edit_{concept.uri}", use_container_width=True):
            edit_uri = concept.uri
        if cols[1].button("Supprimer", key=f"del_{concept.uri}", use_container_width=True):
            delete_uri = concept.uri
        cols[2].write(label)
        cols[3].caption(definition_short)
        cols[4].code(sid, language=None)
        status_colors = {
            ":Active": "🟢",
            ":Provisional": "🟡",
            ":Deprecated": "🔴",
        }
        cols[5].write(f"{status_colors.get(concept.status.value, '')} {status_lbl}")
        cols[6].write(modified)

    return edit_uri, delete_uri, add_clicked
