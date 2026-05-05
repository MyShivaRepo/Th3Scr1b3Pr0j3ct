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
    ":Active":      '<span style="display:inline-block;width:12px;height:12px;background:#a6e3a1;border-radius:50%;vertical-align:middle;"></span>',
    ":Provisional": '<span style="display:inline-block;width:12px;height:12px;background:#f9e2af;border-radius:50%;vertical-align:middle;"></span>',
    ":Deprecated":  '<span style="display:inline-block;width:12px;height:12px;background:#f38ba8;border-radius:50%;vertical-align:middle;"></span>',
}

_CSS = """
<style>
/* ── Bouton Ajouter (primary) ── */
button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #89b4fa, #b4befe) !important;
    color: #1e1e2e !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}

/* ── Tous les boutons secondaires : hauteur compacte ── */
button[data-testid="baseButton-secondary"] {
    min-height: 28px !important;
    height: 28px !important;
    padding: 0 8px !important;
    font-size: 13px !important;
    line-height: 1 !important;
}

/* ── Réduire le gap interne des colonnes ── */
div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* ── Aligner verticalement au centre toutes les lignes ── */
div[data-testid="stHorizontalBlock"] {
    align-items: center !important;
}

/* ── Supprimer la marge basse du wrapper bouton ── */
div[data-testid="stButton"] {
    margin-bottom: 0 !important;
}

/* ── Bouton Éditer ── */
.btn-edit button[data-testid="baseButton-secondary"] {
    border: 1px solid #89b4fa !important;
    color: #89b4fa !important;
    background: transparent !important;
    border-radius: 6px !important;
}
.btn-edit button[data-testid="baseButton-secondary"]:hover {
    background: #89b4fa22 !important;
}

/* ── Bouton Supprimer ── */
.btn-del button[data-testid="baseButton-secondary"] {
    border: 1px solid #f38ba8 !important;
    color: #f38ba8 !important;
    background: transparent !important;
    border-radius: 6px !important;
}
.btn-del button[data-testid="baseButton-secondary"]:hover {
    background: #f38ba822 !important;
}

/* ── Boutons d'en-tête de tri ── */
.sort-header button[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: none !important;
    color: #6c7086 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .7px !important;
    height: 24px !important;
    min-height: 24px !important;
}
.sort-header button[data-testid="baseButton-secondary"]:hover {
    color: #cdd6f4 !important;
    background: transparent !important;
}

/* ── Séparateur de ligne ── */
hr.row-sep {
    margin: 2px 0 !important;
    border: none !important;
    border-top: 1px solid #313244 !important;
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
    n_filtered  = len(filtered)
    n_total     = len(concepts)
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
        'letter-spacing:.7px;color:#6c7086;margin:0;">Actions</p>',
        unsafe_allow_html=True,
    )
    h[1].markdown("&nbsp;", unsafe_allow_html=True)
    for col_key, (col_label, _) in _SORT_COLUMNS.items():
        if h[_COL_IDX[col_key]].button(
            col_label + _sort_icon(col_key),
            key=f"sort_{col_key}",
            use_container_width=True,
        ):
            _on_sort_click(col_key)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="row-sep">', unsafe_allow_html=True)

    # ── Lignes ──
    edit_uri   = None
    delete_uri = None

    for concept in filtered:
        label     = concept.pref_label("fr")
        definition = next((d.value for d in concept.definitions if d.lang == "fr"), "")
        def_short  = definition[:110] + "…" if len(definition) > 110 else definition
        sid        = short_id(concept.uri)
        badge      = _STATUS_BADGE.get(concept.status.value, concept.status.value)
        modified   = concept.modified_at[:10] if concept.modified_at else "—"

        cols = st.columns(_COL_RATIO)

        with cols[0]:
            st.markdown('<div class="btn-edit">', unsafe_allow_html=True)
            if st.button("✏️", key=f"edit_{concept.uri}", use_container_width=True):
                edit_uri = concept.uri
            st.markdown("</div>", unsafe_allow_html=True)

        with cols[1]:
            st.markdown('<div class="btn-del">', unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{concept.uri}", use_container_width=True):
                delete_uri = concept.uri
            st.markdown("</div>", unsafe_allow_html=True)

        cols[2].markdown(
            f'<p style="font-weight:700;font-size:13px;color:#cdd6f4;margin:0;line-height:1.4;">{label}</p>',
            unsafe_allow_html=True,
        )

        _def_html = def_short if def_short else '<em style="color:#45475a">—</em>'
        cols[3].markdown(
            f'<p style="font-size:12px;color:#a6adc8;font-style:italic;margin:0;line-height:1.4;">{_def_html}</p>',
            unsafe_allow_html=True,
        )

        cols[4].markdown(
            f'<code style="font-size:11px;color:#89b4fa;background:#313244;padding:2px 6px;border-radius:4px;">{sid}</code>',
            unsafe_allow_html=True,
        )

        cols[5].markdown(badge, unsafe_allow_html=True)

        cols[6].markdown(
            f'<p style="font-size:11px;color:#6c7086;font-family:monospace;margin:0;">{modified}</p>',
            unsafe_allow_html=True,
        )

        st.markdown('<hr class="row-sep">', unsafe_allow_html=True)

    return edit_uri, delete_uri, add_clicked
