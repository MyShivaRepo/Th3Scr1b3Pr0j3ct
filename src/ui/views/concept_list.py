"""Vue — Liste et recherche des entités conceptuelles."""

from __future__ import annotations
from urllib.parse import quote, unquote

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

_STATUS_COLOR: dict[str, str] = {
    ":Active":      "#a6e3a1",
    ":Provisional": "#f9e2af",
    ":Deprecated":  "#f38ba8",
}

_CSS = """
<style>
/* ── Barre de recherche & filtres ── */
div[data-testid="stTextInput"] input {
    background: #181825 !important;
    border: 1px solid #313244 !important;
    border-radius: 6px !important;
    color: #cdd6f4 !important;
    font-size: 13px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #181825 !important;
    border: 1px solid #313244 !important;
    border-radius: 6px !important;
    color: #cdd6f4 !important;
}

/* ── Bouton Ajouter ── */
button[data-testid="baseButton-primary"] {
    background: #89b4fa !important;
    color: #1e1e2e !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}

/* ── Table principale ── */
.concept-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 4px;
}

/* ── En-têtes ── */
.concept-table thead tr {
    border-bottom: 2px solid #313244;
}
.concept-table thead th {
    padding: 8px 12px;
    text-align: left;
    vertical-align: middle;
    white-space: nowrap;
}
.concept-table thead th a {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .7px;
    color: #585b70;
    text-decoration: none;
    transition: color .15s;
}
.concept-table thead th a:hover  { color: #cdd6f4; }
.concept-table thead th a.active { color: #89b4fa; }
.concept-table thead th a .sort-icon {
    font-size: 10px;
    opacity: .7;
}

/* ── Lignes de données ── */
.concept-table tbody tr.data-row {
    border-bottom: 1px solid #1e1e2e;
    transition: background .1s;
}
.concept-table tbody tr.data-row:hover { background: #181825; }
.concept-table tbody td {
    padding: 7px 12px;
    vertical-align: middle;
}

/* ── Cellules ── */
.cell-actions { width: 68px; white-space: nowrap; }
.cell-label   { font-weight: 600; color: #cdd6f4; min-width: 120px; max-width: 200px; }
.cell-def     { color: #a6adc8; font-style: italic; font-size: 12px; min-width: 160px; max-width: 340px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cell-id      { white-space: nowrap; }
.cell-id code {
    font-family: 'Courier New', monospace;
    font-size: 11px;
    color: #89b4fa;
    background: #313244;
    padding: 2px 7px;
    border-radius: 4px;
}
.cell-date { color: #6c7086; font-size: 11px; font-family: monospace; white-space: nowrap; }

/* ── Boutons d'action (liens HTML) ── */
a.btn-act {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 5px;
    text-decoration: none;
    font-size: 13px;
    transition: background .15s;
    margin-right: 3px;
}
a.btn-edit { border: 1px solid #89b4fa44; }
a.btn-edit:hover { background: #89b4fa22; }
a.btn-del  { border: 1px solid #f38ba844; }
a.btn-del:hover  { background: #f38ba822; }

/* ── Pastille statut ── */
.status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    vertical-align: middle;
}

/* ── Ligne de confirmation suppression ── */
.concept-table tbody tr.confirm-row td {
    padding: 8px 16px;
    background: #1e1218;
    border-left: 3px solid #f38ba8;
    border-bottom: 1px solid #313244;
}
.confirm-msg { color: #f38ba8; font-weight: 700; font-size: 13px; }
.confirm-sub { color: #6c7086; font-size: 12px; margin-left: 8px; }
a.btn-confirm {
    display: inline-flex; align-items: center;
    padding: 3px 12px; border-radius: 5px;
    text-decoration: none; font-size: 12px; font-weight: 600;
    margin-left: 14px;
    background: #a6e3a111; border: 1px solid #a6e3a1;
    color: #a6e3a1; transition: background .15s;
}
a.btn-confirm:hover { background: #a6e3a133; }
a.btn-cancel {
    display: inline-flex; align-items: center;
    padding: 3px 12px; border-radius: 5px;
    text-decoration: none; font-size: 12px; font-weight: 600;
    margin-left: 6px;
    background: transparent; border: 1px solid #45475a;
    color: #585b70; transition: background .15s;
}
a.btn-cancel:hover { background: #313244; color: #cdd6f4; }
</style>
"""


def _sort_icon(col_key: str) -> str:
    if st.session_state.get("sort_col") != col_key:
        return "⇅"
    return "▲" if st.session_state.get("sort_asc", True) else "▼"


def _on_sort_click(col_key: str) -> None:
    if st.session_state.get("sort_col") == col_key:
        st.session_state["sort_asc"] = not st.session_state.get("sort_asc", True)
    else:
        st.session_state["sort_col"] = col_key
        st.session_state["sort_asc"] = True


def _sort_link(col_key: str, col_label: str) -> str:
    icon    = _sort_icon(col_key)
    is_act  = st.session_state.get("sort_col") == col_key
    cls     = "active" if is_act else ""
    return (
        f'<a href="?action=sort&col={col_key}" class="{cls}">'
        f'{col_label}<span class="sort-icon">{icon}</span></a>'
    )


def render_concept_list(concepts: list[Concept]) -> tuple[str | None, str | None, bool]:
    """Affiche la liste filtrée et triable des entités.

    Retourne (uri_à_éditer, uri_à_supprimer, ajouter_cliqué).
    """
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Actions depuis les query params (clics sur liens HTML) ──
    params     = st.query_params
    action     = params.get("action")
    action_uri = unquote(params.get("uri", ""))

    if action == "edit" and action_uri:
        st.query_params.clear()
        return action_uri, None, False

    if action == "delete" and action_uri:
        st.query_params.clear()
        st.session_state.pop("confirm_delete_uri", None)
        return None, action_uri, False

    if action == "confirm_delete" and action_uri:
        st.session_state["confirm_delete_uri"] = action_uri
        st.query_params.clear()
        st.rerun()

    if action == "cancel_delete":
        st.session_state.pop("confirm_delete_uri", None)
        st.query_params.clear()
        st.rerun()

    if action == "sort" and params.get("col"):
        _on_sort_click(params.get("col"))
        st.query_params.clear()
        st.rerun()

    # ── Barre de recherche & filtres ──
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input(
            "Rechercher", placeholder="🔍  Filtrer par label…",
            key="search_text", label_visibility="collapsed",
        )
    with col2:
        status_options = ["Tous"] + [ConceptStatus.label(s) for s in ConceptStatus]
        status_filter = st.selectbox(
            "Statut", status_options, key="status_filter", label_visibility="collapsed",
        )

    # ── Filtrage ──
    filtered = concepts
    if search:
        sl = search.lower()
        filtered = [c for c in filtered if any(sl in lbl.lower() for lbl in c.all_labels())]
    if status_filter != "Tous":
        ts = next(s for s in ConceptStatus if ConceptStatus.label(s) == status_filter)
        filtered = [c for c in filtered if c.status == ts]

    # ── Tri ──
    sort_col = st.session_state.get("sort_col", "label")
    sort_asc = st.session_state.get("sort_asc", True)
    sort_fn  = _SORT_COLUMNS.get(sort_col, _SORT_COLUMNS["label"])[1]
    filtered = sorted(filtered, key=sort_fn, reverse=not sort_asc)

    # ── Titre + bouton Ajouter ──
    n_filtered  = len(filtered)
    n_total     = len(concepts)
    count_label = f"({n_filtered})" if n_filtered == n_total else f"({n_filtered} / {n_total})"

    t_col, b_col = st.columns([5, 1])
    t_col.subheader(f"Référentiel d'entités {count_label}")
    add_clicked = b_col.button("➕ Ajouter", use_container_width=True, type="primary")

    if not filtered:
        st.info("Aucune entité ne correspond aux critères de recherche.")
        return None, None, add_clicked

    # ── Table HTML ──
    confirm_uri = st.session_state.get("confirm_delete_uri")

    thead = f"""<thead><tr>
        <th class="cell-actions"></th>
        <th>{_sort_link("label",      "Label (fr)")}</th>
        <th>{_sort_link("definition", "Définition (fr)")}</th>
        <th>{_sort_link("id",         "ID court")}</th>
        <th>{_sort_link("status",     "Statut")}</th>
        <th>{_sort_link("modified",   "Modifié le")}</th>
    </tr></thead>"""

    rows: list[str] = []
    for concept in filtered:
        label     = concept.pref_label("fr")
        definition = next((d.value for d in concept.definitions if d.lang == "fr"), "")
        def_short  = definition[:95] + "…" if len(definition) > 95 else definition
        sid        = short_id(concept.uri)
        dot_color  = _STATUS_COLOR.get(concept.status.value, "#6c7086")
        modified   = concept.modified_at[:10] if concept.modified_at else "—"
        uri_enc    = quote(concept.uri, safe="")

        rows.append(f"""<tr class="data-row">
            <td class="cell-actions">
                <a href="?action=edit&uri={uri_enc}" class="btn-act btn-edit" title="Éditer">✏️</a>
                <a href="?action=confirm_delete&uri={uri_enc}" class="btn-act btn-del" title="Supprimer">🗑️</a>
            </td>
            <td class="cell-label">{label}</td>
            <td class="cell-def">{def_short if def_short else '<em style="color:#45475a">—</em>'}</td>
            <td class="cell-id"><code>{sid}</code></td>
            <td><span class="status-dot" style="background:{dot_color};"></span></td>
            <td class="cell-date">{modified}</td>
        </tr>""")

        if confirm_uri == concept.uri:
            del_enc = quote(concept.uri, safe="")
            rows.append(f"""<tr class="confirm-row">
                <td colspan="6">
                    <span class="confirm-msg">⚠️ Supprimer « {label} » ?</span>
                    <span class="confirm-sub">Cette action est irréversible.</span>
                    <a href="?action=delete&uri={del_enc}" class="btn-confirm">✅ Confirmer</a>
                    <a href="?action=cancel_delete" class="btn-cancel">❌ Annuler</a>
                </td>
            </tr>""")

    st.markdown(
        f'<table class="concept-table">{thead}<tbody>{"".join(rows)}</tbody></table>',
        unsafe_allow_html=True,
    )

    return None, None, add_clicked
