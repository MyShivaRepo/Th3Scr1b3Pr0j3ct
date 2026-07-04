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

_LANGUAGES = ["fr", "en", "de", "es", "it", "pt", "nl", "ar", "zh", "ja", "la"]

_INVERSE: dict[RelationType, RelationType] = {
    RelationType.BROADER:    RelationType.NARROWER,
    RelationType.NARROWER:   RelationType.BROADER,
    RelationType.RELATED:    RelationType.RELATED,
    RelationType.IS_PART_OF: RelationType.HAS_PART,
    RelationType.HAS_PART:   RelationType.IS_PART_OF,
}

_STATUS_COLOR = {
    ConceptStatus.ACTIVE:      ("#a6e3a1", "Actif"),
    ConceptStatus.PROVISIONAL: ("#f9e2af", "Provisoire"),
    ConceptStatus.DEPRECATED:  ("#f38ba8", "Déprécié"),
}

_EDIT_CSS = """
<style>
/* ── Expanders ── */
details[data-testid="stExpander"] {
    border: 1px solid #313244 !important;
    border-radius: 8px !important;
    background: #181825 !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
details[data-testid="stExpander"] > summary {
    background: #1e1e2e !important;
    padding: 10px 14px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #cdd6f4 !important;
    border-bottom: 1px solid #1e1e2e !important;
    cursor: pointer !important;
}
details[data-testid="stExpander"][open] > summary {
    border-bottom: 1px solid #313244 !important;
}
details[data-testid="stExpander"] > summary p {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #cdd6f4 !important;
}

/* ── Inputs & textareas ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #11111b !important;
    border: 1px solid #313244 !important;
    border-radius: 6px !important;
    color: #cdd6f4 !important;
    font-size: 13px !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #89b4fa !important;
    box-shadow: 0 0 0 2px #89b4fa22 !important;
}

/* ── Selectboxes ── */
div[data-testid="stSelectbox"] > div > div {
    background: #11111b !important;
    border: 1px solid #313244 !important;
    border-radius: 6px !important;
    color: #cdd6f4 !important;
    font-size: 13px !important;
}

/* ── Labels des champs ── */
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stCheckbox"] label {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
    color: #585b70 !important;
}

/* ── Boutons ✕ de suppression ── */
.del-btn button[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: 1px solid #f38ba844 !important;
    color: #f38ba8 !important;
    border-radius: 5px !important;
    font-size: 12px !important;
    min-height: 28px !important;
    height: 28px !important;
    padding: 0 10px !important;
}
.del-btn button[data-testid="baseButton-secondary"]:hover {
    background: #f38ba811 !important;
    border-color: #f38ba8 !important;
}

/* ── Boutons "Ajouter" (form submit) ── */
div[data-testid="stFormSubmitButton"] button {
    background: transparent !important;
    border: 1px solid #89b4fa !important;
    color: #89b4fa !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    min-height: 32px !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background: #89b4fa11 !important;
}

/* ── Formulaires d'ajout ── */
div[data-testid="stForm"] {
    background: #11111b !important;
    border: 1px solid #313244 !important;
    border-radius: 8px !important;
    padding: 12px 14px !important;
    margin-top: 10px !important;
}

/* ── Bouton Sauvegarder ── */
button[data-testid="baseButton-primary"] {
    background: #89b4fa !important;
    color: #1e1e2e !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}

/* ── Divider ── */
hr[data-testid="stDivider"] { border-color: #313244 !important; }

/* ── Alignement vertical colonnes ── */
div[data-testid="stHorizontalBlock"] { align-items: center !important; }
div[data-testid="stButton"] { margin-bottom: 0 !important; }
</style>
"""


def _lang_idx(lang: str) -> int:
    try:
        return _LANGUAGES.index(lang)
    except ValueError:
        return 0


def _header_card(concept: Concept) -> None:
    color, label = _STATUS_COLOR.get(concept.status, ("#6c7086", "?"))
    version = concept.uri.split("#")[-1] if "#" in concept.uri else "v?"
    sid = short_id(concept.uri)
    st.markdown(f"""
    <div style="background:#181825;border:1px solid #313244;border-radius:10px;
                padding:14px 18px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <span style="font-size:20px;font-weight:800;color:#cdd6f4;">
                {concept.pref_label("fr")}
            </span>
            <span style="background:{color}22;border:1px solid {color}88;color:{color};
                         padding:2px 10px;border-radius:12px;font-size:11px;font-weight:700;">
                {label}
            </span>
            <span style="background:#313244;color:#89b4fa;font-family:monospace;
                         padding:2px 8px;border-radius:4px;font-size:11px;">
                {sid}
            </span>
            <span style="color:#6c7086;font-size:11px;font-family:monospace;">{version}</span>
        </div>
        <div style="margin-top:6px;font-size:11px;color:#45475a;
                    font-family:monospace;word-break:break-all;">
            {concept.uri}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_concept_edit(concept: Concept, all_concepts: list[Concept]) -> bool:
    """Affiche le formulaire d'édition complet. Retourne True si des modifications ont été sauvegardées."""
    st.markdown(_EDIT_CSS, unsafe_allow_html=True)
    _header_card(concept)

    # ---- Statut ----
    with st.expander("🏷️  Statut", expanded=True):
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
    with st.expander("🔤  Labels (prefLabel / altLabel)", expanded=True):
        _edit_labels(concept)

    # ---- Définitions ----
    with st.expander("📝  Définitions (skos:definition)"):
        _edit_definitions(concept)

    # ---- Notes ----
    with st.expander("💬  Notes (skos:note / skos:scopeNote)"):
        _edit_notes(concept)

    # ---- Relations ----
    with st.expander("🔗  Relations à d'autres entités"):
        _edit_relations(concept, all_concepts)

    # ---- Actes de représentation ----
    with st.expander("🖼️  Actes de représentation"):
        render_representation_section(concept, all_concepts)

    # ---- Mappings ----
    with st.expander("🗺️  Mappings inter-référentiels"):
        _edit_mappings(concept)

    # ---- Bouton sauvegarde global ----
    st.divider()
    if st.button("💾  Sauvegarder les modifications", type="primary", key=f"save_{concept.uri}", use_container_width=True):
        concept.uri = increment_version(concept.uri)
        concept.modified_at = datetime.now(timezone.utc).isoformat()
        st.toast(f"✅ Entité sauvegardée — version {concept.uri.split('#')[-1]}", icon="💾")
        return True

    return False


# ---------------------------------------------------------------------------
# Sections d'édition internes
# ---------------------------------------------------------------------------

def _edit_labels(concept: Concept) -> bool:
    modified = False
    indices_to_delete = []
    for i, lbl in enumerate(concept.labels):
        cols = st.columns([2, 1, 1, 1])
        new_val  = cols[0].text_input("Valeur", value=lbl.value, key=f"lbl_val_{concept.uri}_{i}")
        new_lang = cols[1].selectbox("Langue", _LANGUAGES, index=_lang_idx(lbl.lang), key=f"lbl_lang_{concept.uri}_{i}")
        new_pref = cols[2].checkbox("Préféré", value=lbl.preferred, key=f"lbl_pref_{concept.uri}_{i}")
        with cols[3]:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"lbl_del_{concept.uri}_{i}", use_container_width=True):
                indices_to_delete.append(i)
                modified = True
            st.markdown("</div>", unsafe_allow_html=True)
        if new_val != lbl.value or new_lang != lbl.lang or new_pref != lbl.preferred:
            lbl.value, lbl.lang, lbl.preferred = new_val, new_lang, new_pref
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.labels.pop(i)

    with st.form(f"form_add_label_{concept.uri}"):
        c1, c2, c3 = st.columns([3, 1, 1])
        new_lbl  = c1.text_input("Nouveau label", key=f"new_lbl_{concept.uri}")
        new_lang = c2.selectbox("Langue", _LANGUAGES, index=0, key=f"new_lang_{concept.uri}")
        new_pref = c3.checkbox("Préféré", value=False, key=f"new_pref_{concept.uri}")
        if st.form_submit_button("➕  Ajouter"):
            if new_lbl.strip():
                concept.labels.append(LabelAssertion(value=new_lbl.strip(), lang=new_lang, preferred=new_pref))
                modified = True
    return modified


def _edit_definitions(concept: Concept) -> bool:
    modified = False
    indices_to_delete = []
    for i, defn in enumerate(concept.definitions):
        cols = st.columns([4, 1, 1])
        new_val  = cols[0].text_area("Texte", value=defn.value, key=f"def_val_{concept.uri}_{i}", height=100)
        new_lang = cols[1].selectbox("Langue", _LANGUAGES, index=_lang_idx(defn.lang), key=f"def_lang_{concept.uri}_{i}")
        with cols[2]:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"def_del_{concept.uri}_{i}", use_container_width=True):
                indices_to_delete.append(i)
                modified = True
            st.markdown("</div>", unsafe_allow_html=True)
        if new_val != defn.value or new_lang != defn.lang:
            defn.value, defn.lang = new_val, new_lang
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.definitions.pop(i)

    with st.form(f"form_add_def_{concept.uri}"):
        c1, c2 = st.columns([4, 1])
        new_def  = c1.text_area("Nouvelle définition", key=f"new_def_{concept.uri}", height=80)
        new_lang = c2.selectbox("Langue", _LANGUAGES, index=0, key=f"new_deflang_{concept.uri}")
        if st.form_submit_button("➕  Ajouter"):
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
        new_val   = cols[0].text_area(f"[{note_type}]", value=note.value, key=f"note_val_{concept.uri}_{i}", height=80)
        new_lang  = cols[1].selectbox("Langue", _LANGUAGES, index=_lang_idx(note.lang), key=f"note_lang_{concept.uri}_{i}")
        new_scope = cols[2].checkbox("scopeNote", value=note.scope, key=f"note_scope_{concept.uri}_{i}")
        with cols[3]:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"note_del_{concept.uri}_{i}", use_container_width=True):
                indices_to_delete.append(i)
                modified = True
            st.markdown("</div>", unsafe_allow_html=True)
        if new_val != note.value or new_lang != note.lang or new_scope != note.scope:
            note.value, note.lang, note.scope = new_val, new_lang, new_scope
            modified = True
    for i in sorted(indices_to_delete, reverse=True):
        concept.notes.pop(i)

    with st.form(f"form_add_note_{concept.uri}"):
        c1, c2, c3 = st.columns([4, 1, 1])
        new_note  = c1.text_area("Nouvelle note", key=f"new_note_{concept.uri}", height=60)
        new_lang  = c2.selectbox("Langue", _LANGUAGES, index=0, key=f"new_notelang_{concept.uri}")
        new_scope = c3.checkbox("scopeNote", value=False, key=f"new_scope_{concept.uri}")
        if st.form_submit_button("➕  Ajouter"):
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
        cols[0].markdown(
            f'<code style="font-size:11px;color:#cba6f7;background:#313244;padding:2px 7px;border-radius:4px;">'
            f'{rel.relation_type.value}</code>',
            unsafe_allow_html=True,
        )
        cols[1].markdown(
            f'<span style="color:#6c7086;margin-right:4px;">→</span>'
            f'<span style="color:#cdd6f4;font-size:13px;">{target_label}</span>',
            unsafe_allow_html=True,
        )
        with cols[2]:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"rel_del_{concept.uri}_{i}", use_container_width=True):
                indices_to_delete.append(i)
                modified = True
            st.markdown("</div>", unsafe_allow_html=True)
    for i in sorted(indices_to_delete, reverse=True):
        concept.relations.pop(i)

    if other_concepts:
        with st.form(f"form_add_rel_{concept.uri}"):
            type_options   = {rt.value: rt for rt in RelationType}
            target_options = {f"{c.pref_label('fr')} [{short_id(c.uri)}]": c.uri for c in other_concepts}
            c1, c2 = st.columns(2)
            chosen_type   = c1.selectbox("Type de relation", list(type_options.keys()), key=f"rel_type_{concept.uri}")
            chosen_target = c2.selectbox("Entité cible", list(target_options.keys()), key=f"rel_target_{concept.uri}")
            if st.form_submit_button("➕  Ajouter la relation"):
                rel_type   = type_options[chosen_type]
                target_uri = target_options[chosen_target]
                concept.relations.append(RelationAssertion(relation_type=rel_type, target_uri=target_uri))
                inv_type = _INVERSE.get(rel_type)
                if inv_type:
                    target_concept = next((c for c in all_concepts if c.uri == target_uri), None)
                    if target_concept:
                        already = any(
                            r.relation_type == inv_type and r.target_uri == concept.uri
                            for r in target_concept.relations
                        )
                        if not already:
                            target_concept.relations.append(
                                RelationAssertion(relation_type=inv_type, target_uri=concept.uri)
                            )
                modified = True
    else:
        st.markdown(
            '<p style="color:#585b70;font-size:12px;font-style:italic;">'
            'Créez au moins une autre entité pour ajouter des relations.</p>',
            unsafe_allow_html=True,
        )
    return modified


def _edit_mappings(concept: Concept) -> bool:
    modified = False
    indices_to_delete = []
    for i, mapping in enumerate(concept.mappings):
        cols = st.columns([2, 4, 1])
        cols[0].markdown(
            f'<code style="font-size:11px;color:#cba6f7;background:#313244;padding:2px 7px;border-radius:4px;">'
            f'{mapping.mapping_type.value}</code>',
            unsafe_allow_html=True,
        )
        cols[1].markdown(
            f'<span style="color:#a6adc8;font-size:12px;font-family:monospace;">{mapping.target_uri}</span>',
            unsafe_allow_html=True,
        )
        with cols[2]:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"map_del_{concept.uri}_{i}", use_container_width=True):
                indices_to_delete.append(i)
                modified = True
            st.markdown("</div>", unsafe_allow_html=True)
    for i in sorted(indices_to_delete, reverse=True):
        concept.mappings.pop(i)

    with st.form(f"form_add_mapping_{concept.uri}"):
        type_options = {mt.value: mt for mt in MappingType}
        c1, c2 = st.columns([1, 3])
        chosen_type = c1.selectbox("Type", list(type_options.keys()), key=f"map_type_{concept.uri}")
        target_uri  = c2.text_input("URI cible", key=f"map_target_{concept.uri}")
        if st.form_submit_button("➕  Ajouter le mapping"):
            if target_uri.strip():
                concept.mappings.append(
                    MappingAssertion(mapping_type=type_options[chosen_type], target_uri=target_uri.strip())
                )
                modified = True
    return modified
