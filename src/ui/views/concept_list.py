"""Vue — Liste et recherche des entités conceptuelles."""

from __future__ import annotations

import streamlit as st

from src.model.concept import Concept, ConceptStatus
from src.model.identity import short_id

_SORT_COLUMNS: dict[str, tuple[str, callable]] = {
    "label":      ("Label (fr)",       lambda c: c.pref_label("fr").lower()),
    "definition": ("Définition (fr)",  lambda c: next((d.value for d in c.definitions if d.lang == "fr"), "").lower()),
    "id":         ("ID court",         lambda c: short_id(c.uri).lower()),
    "status":     ("Statut",           lambda c: c.status.value),
    "modified":   ("Modifié le",       lambda c: c.modified_at or ""),
}

_STATUS_BADGE: dict[str, str] = {
    ":Active":      '<span style="display:inline-block;width:14px;height:14px;'
                    'background:#a6e3a1;border-radius:50%;"></span>',
    ":Provisional": '<span style="display:inline-block;width:14px;height:14px;'
                    'background:#f9e2af;border-radius:50%;"></span>',
    ":Deprecated":  '<span style="display:inline-block;width:14px;height:14px;'
                    'background:#f38ba8;border-radius:50%;"></span>',
}

_CSS = """
<style>
/* ── Barre de recherche & filtres ── */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
}

/* ── Bouton Ajouter ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #89b4fa, #b4befe) !important;
    color: #1e1e2e !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: .3px !important;
}

/* ── Boutons d'en-tête de tri ── */
.sort-header button {
    background: transparent !important;
    border: none !important;
    color: #6c7086 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .7px !important;
    padding: 4px 0 !important;
}
.sort-header button:hover {
    color: #cdd6f4 !important;
}

/* ── Boutons Éditer / Supprimer ── */
.btn-edit button {
    background: transparent !important;
    border: 1px solid #89b4fa !important;
    color: #89b4fa !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 2px 8px !important;
    transition: background .15s !important;
}
.btn-edit button:hover {
    background: #89b4fa22 !important;
}
.btn-del button {
    background: transparent !important;
    border: 1px solid #f38ba8 !important;
    color: #f38ba8 !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 2px 8px !important;
    transition: background .15s !important;
}
.btn-del button:hover {
    background: #f38ba822 !important;
}
</style>
"""

_COL_RATIO = [1, 1, 3, 4, 1, 1, 2]
_COL_IDX   = {"label": 2, "definition": 3, "id": 4, "status": 5, "modified": 6}


def _sort_icon(col_key: str) -> str:
    if st.session_state.get("sort_col") != col_key:
        return " ⇅"
    return " ▲" if st.session_state.get("sort_asc", True) else " ▼"


def _on_sort_click(col_key: str) -> None:
    if st.session_state.get("sort_col") == col_key:
        st.session_state["sort_asc"] = not st.session_state.get("sort_asc", True)
    else:
        st.session_state["sort_col"] = col_key
        st.session_state["sort_asc"] = True


def render_concept_list(concepts: list[Concept]) -> tuple[str | None, str | None, bool]:
    """Affiche la liste filtrée et triable des entités.

    Retourne (uri_à_éditer, uri_à_supprimer, ajouter_cliqué).
    """
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Barre de recherche & filtres ──
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Rechercher", placeholder="Filtrer par label…", key="search_text")
    with col2:
        status_options = ["Tous"] + [ConceptStatus.label(s) for s in ConceptStatus]
        status_filter = st.selectbox("Statut", status_options, key="status_filter")

    # ── Filtrage ──
    filtered = concepts
    if search:
        search_lower = search.lower()
        filtered = [c for c in filtered if any(search_lower in lbl.lower() for lbl in c.all_labels())]
    if status_filter != "Tous":
        target_status = next(s for s in ConceptStatus if ConceptStatus.label(s) == status_filter)
        filtered = [c for c in filtered if c.status == target_status]

    # ── Tri ──
    sort_col = st.session_state.get("sort_col", "label")
    sort_asc = st.session_state.get("sort_asc", True)
    sort_fn  = _SORT_COLUMNS.get(sort_col, _SORT_COLUMNS["label"])[1]
    filtered = sorted(filtered, key=sort_fn, reverse=not sort_asc)

    # ── Titre + bouton Ajouter ──
    n_filtered = len(filtered)
    n_total    = len(concepts)
    count_label = f"({n_filtered})" if n_filtered == n_total else f"({n_filtered} / {n_total})"

    title_col, btn_col = st.columns([5, 1])
    title_col.subheader(f"Référentiel d'entités {count_label}")
    add_clicked = btn_col.button("➕ Ajouter", use_container_width=True, type="primary")

    if not filtered:
        st.info("Aucune entité ne correspond aux critères de recherche.")
        return None, None, add_clicked

    st.divider()

    # ── En-têtes triables ──
    st.markdown('<div class="sort-header">', unsafe_allow_html=True)
    h = st.columns(_COL_RATIO)
    h[0].markdown(
        '<p style="font-size:11px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:.7px;color:#6c7086;margin:0;padding:4px 0;">Action</p>',
        unsafe_allow_html=True,
    )
    h[1].markdown(
        '<p style="font-size:11px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:.7px;color:#6c7086;margin:0;padding:4px 0;">&nbsp;</p>',
        unsafe_allow_html=True,
    )
    for col_key, (col_label, _) in _SORT_COLUMNS.items():
        if h[_COL_IDX[col_key]].button(
            col_label + _sort_icon(col_key),
            key=f"sort_{col_key}",
            use_container_width=True,
        ):
            _on_sort_click(col_key)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # ── Lignes ──
    edit_uri   = None
    delete_uri = None

    for concept in filtered:
        label      = concept.pref_label("fr")
        definition = next((d.value for d in concept.definitions if d.lang == "fr"), "")
        def_short  = definition[:110] + "…" if len(definition) > 110 else definition
        sid        = short_id(concept.uri)
        badge      = _STATUS_BADGE.get(concept.status.value, concept.status.value)
        modified   = concept.modified_at[:10] if concept.modified_at else "—"

        with st.container(border=True):
            cols = st.columns(_COL_RATIO)

            # Bouton Éditer
            with cols[0]:
                st.markdown('<div class="btn-edit">', unsafe_allow_html=True)
                if st.button("✏️", key=f"edit_{concept.uri}", use_container_width=True):
                    edit_uri = concept.uri
                st.markdown("</div>", unsafe_allow_html=True)

            # Bouton Supprimer
            with cols[1]:
                st.markdown('<div class="btn-del">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{concept.uri}", use_container_width=True):
                    delete_uri = concept.uri
                st.markdown("</div>", unsafe_allow_html=True)

            # Label
            cols[2].markdown(
                f'<p style="font-weight:700;font-size:14px;color:#cdd6f4;margin:0;'
                f'line-height:1.5;">{label}</p>',
                unsafe_allow_html=True,
            )

            # Définition
            _def_html = def_short if def_short else '<em style="color:#45475a">—</em>'
            cols[3].markdown(
                f'<p style="font-size:12px;color:#a6adc8;font-style:italic;margin:0;'
                f'line-height:1.5;">{_def_html}</p>',
                unsafe_allow_html=True,
            )

            # ID court
            cols[4].markdown(
                f'<code style="font-size:12px;color:#89b4fa;background:#313244;'
                f'padding:2px 7px;border-radius:5px;">{sid}</code>',
                unsafe_allow_html=True,
            )

            # Statut
            cols[5].markdown(badge, unsafe_allow_html=True)

            # Date
            cols[6].markdown(
                f'<p style="font-size:12px;color:#6c7086;font-family:monospace;margin:0;">'
                f'{modified}</p>',
                unsafe_allow_html=True,
            )

    return edit_uri, delete_uri, add_clicked
