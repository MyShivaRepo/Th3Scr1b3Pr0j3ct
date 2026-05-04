"""Application Streamlit principale — Th3Sr1b3Pr0j3ct."""

from __future__ import annotations

import streamlit as st

from src.seed.load_concepts import get_store, load_seed_if_empty
from src.ui.views.concept_create import render_concept_create
from src.ui.views.concept_edit import render_concept_edit
from src.ui.views.concept_list import render_concept_list

# ---------------------------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Th3Sr1b3Pr0j3ct",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Initialisation du store (persisté dans session_state)
# ---------------------------------------------------------------------------
if "store" not in st.session_state:
    st.session_state.store = get_store()

if "concepts" not in st.session_state:
    st.session_state.concepts = load_seed_if_empty(st.session_state.store)

if "view" not in st.session_state:
    st.session_state.view = "list"

if "selected_uri" not in st.session_state:
    st.session_state.selected_uri = None


def save_concepts() -> None:
    """Sauvegarde la liste courante dans le store."""
    st.session_state.store.save(st.session_state.concepts)


# ---------------------------------------------------------------------------
# Barre latérale
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("📖 Th3Sr1b3Pr0j3ct")
    st.caption("Référentiel conceptuel — Itération 1")
    st.divider()

    if st.button("📋 Liste des entités", use_container_width=True):
        st.session_state.view = "list"
        st.session_state.selected_uri = None

    if st.button("➕ Nouvelle entité", use_container_width=True):
        st.session_state.view = "create"
        st.session_state.selected_uri = None

    st.divider()
    total = len(st.session_state.concepts)
    st.metric("Entités", total)


# ---------------------------------------------------------------------------
# Routage des vues
# ---------------------------------------------------------------------------
view = st.session_state.view

if view == "list":
    selected = render_concept_list(st.session_state.concepts)
    if selected:
        st.session_state.selected_uri = selected
        st.session_state.view = "edit"
        st.rerun()

elif view == "create":
    new_concept = render_concept_create()
    if new_concept is not None:
        st.session_state.concepts.append(new_concept)
        save_concepts()
        st.session_state.view = "list"
        st.rerun()

elif view == "edit":
    uri = st.session_state.selected_uri
    concept = next((c for c in st.session_state.concepts if c.uri == uri), None)

    if concept is None:
        # L'URI peut avoir changé après incrémentation de version — chercher par base
        base = uri.split("#")[0]
        concept = next(
            (c for c in st.session_state.concepts if c.uri.split("#")[0] == base), None
        )

    if concept is None:
        st.error("Entité introuvable.")
        st.session_state.view = "list"
        st.rerun()
    else:
        if st.button("← Retour à la liste"):
            st.session_state.view = "list"
            st.session_state.selected_uri = None
            st.rerun()

        saved = render_concept_edit(concept, st.session_state.concepts)
        if saved:
            # Mettre à jour l'URI sélectionnée après incrémentation de version
            st.session_state.selected_uri = concept.uri
            save_concepts()
            st.rerun()
