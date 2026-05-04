"""Chargement du référentiel initial depuis le fichier seed Turtle."""

from __future__ import annotations

from pathlib import Path

from src.model.concept import Concept
from src.storage.turtle_store import TurtleStore

SEED_PATH = Path(__file__).parent.parent.parent / "data" / "seed" / "bernard_concepts.ttl"
STORE_PATH = Path(__file__).parent.parent.parent / "data" / "concepts.ttl"


def load_seed_if_empty(store: TurtleStore) -> list[Concept]:
    """Charge le seed si le store principal est vide, puis sauvegarde.

    Retourne la liste finale des concepts (seed ou existants).
    """
    existing = store.load()
    if existing:
        return existing

    if not SEED_PATH.exists():
        return []

    seed_concepts = store.load_from_file(SEED_PATH)
    if seed_concepts:
        store.save(seed_concepts)
    return seed_concepts


def get_store() -> TurtleStore:
    """Retourne l'instance du store principal."""
    return TurtleStore(STORE_PATH)
