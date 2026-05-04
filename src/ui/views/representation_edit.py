"""Vue — Gestion des actes de représentation (couche 2.3.3)."""

from __future__ import annotations

import streamlit as st

from src.model.concept import Concept
from src.model.identity import short_id
from src.model.representation import RepresentationAct, RepresentationKind


def render_representation_section(
    concept: Concept,
    all_concepts: list[Concept],
) -> bool:
    """Affiche et édite les actes de représentation d'une entité.

    Retourne True si des modifications ont été effectuées.
    """
    modified = False
    st.markdown("##### Actes de représentation (couche 2.3.3)")
    st.caption(
        "Une représentation est toujours une entité à part entière. "
        "La récursion sujet → objet est non bornée."
    )

    # Actes de représentation sortants (self = sujet)
    st.markdown("**Représentations sortantes** *(cette entité est représentée par…)*")
    indices_to_delete = []
    for i, act in enumerate(concept.representations_out):
        target_label = _find_label(act.target_uri, all_concepts)
        with st.expander(
            f"[{RepresentationKind.label(act.kind)}] → {target_label} ({short_id(act.target_uri)}…)"
        ):
            st.write(f"**Type :** {RepresentationKind.label(act.kind)}")
            st.write(f"**Cible :** `{act.target_uri}`")
            if act.context:
                st.write(f"**Contexte :** {act.context}")
            if act.created_by:
                st.write(f"**Auteur :** {act.created_by}")
            if act.created_on:
                st.write(f"**Date :** {act.created_on}")
            if st.button("Supprimer", key=f"del_repr_{concept.uri}_{i}"):
                indices_to_delete.append(i)
                modified = True

    for i in sorted(indices_to_delete, reverse=True):
        concept.representations_out.pop(i)

    # Actes de représentation entrants (self = objet)
    incoming = [
        (c, act)
        for c in all_concepts
        for act in c.representations_out
        if act.target_uri == concept.uri and c.uri != concept.uri
    ]
    if incoming:
        st.markdown("**Représentations entrantes** *(cette entité représente…)*")
        for src_concept, act in incoming:
            src_label = src_concept.pref_label("fr")
            st.info(
                f"← **{src_label}** ({short_id(src_concept.uri)}…) "
                f"— type : {RepresentationKind.label(act.kind)}"
            )

    # Formulaire d'ajout
    st.markdown("**Ajouter un acte de représentation**")
    other_concepts = [c for c in all_concepts if c.uri != concept.uri]
    if not other_concepts:
        st.caption("Créez au moins une autre entité pour ajouter une représentation.")
        return modified

    kind_options = {RepresentationKind.label(k): k for k in RepresentationKind}
    target_options = {
        f"{c.pref_label('fr')} [{short_id(c.uri)}…]": c.uri for c in other_concepts
    }

    with st.form(f"form_repr_{concept.uri}"):
        chosen_kind_label = st.selectbox(
            "Type de représentation", list(kind_options.keys()), key=f"repr_kind_{concept.uri}"
        )
        chosen_target_label = st.selectbox(
            "Entité cible (l'objet / la représentation)",
            list(target_options.keys()),
            key=f"repr_target_{concept.uri}",
        )
        context = st.text_input("Contexte (optionnel)", key=f"repr_ctx_{concept.uri}")
        created_by = st.text_input("Auteur de la représentation (optionnel)", key=f"repr_by_{concept.uri}")
        created_on = st.text_input("Date (AAAA-MM-JJ, optionnel)", key=f"repr_on_{concept.uri}")

        if st.form_submit_button("Ajouter cet acte de représentation"):
            concept.representations_out.append(
                RepresentationAct(
                    target_uri=target_options[chosen_target_label],
                    kind=kind_options[chosen_kind_label],
                    context=context.strip() or None,
                    created_by=created_by.strip() or None,
                    created_on=created_on.strip() or None,
                )
            )
            modified = True
            st.success("Acte de représentation ajouté.")

    return modified


def _find_label(uri: str, concepts: list[Concept]) -> str:
    """Retourne le label préféré d'une URI, ou l'URI tronquée si introuvable."""
    for c in concepts:
        if c.uri == uri:
            return c.pref_label("fr")
    return uri[:30] + "…"
