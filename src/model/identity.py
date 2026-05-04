"""Couche 1 — Identité : génération et gestion des URI opaques persistants."""

from __future__ import annotations

import re
import uuid


NAMESPACE = "scribe"
URN_PREFIX = f"urn:concept:{NAMESPACE}:"
_VERSION_RE = re.compile(r"^v(\d+)$")


def generate_uri() -> str:
    """Génère un nouvel URI opaque au format urn:concept:scribe:{uuid}#v1."""
    concept_id = str(uuid.uuid4()).upper()
    return f"{URN_PREFIX}{concept_id}#v1"


def extract_uuid(uri: str) -> str:
    """Extrait le composant UUID d'un URI (sans version ni préfixe)."""
    base = uri.split("#")[0]
    if not base.startswith(URN_PREFIX):
        raise ValueError(f"URI invalide — préfixe attendu : {URN_PREFIX!r}")
    return base[len(URN_PREFIX):]


def extract_version(uri: str) -> int:
    """Extrait le numéro de version d'un URI versionné (ex. #v3 → 3)."""
    if "#" not in uri:
        raise ValueError(f"URI sans version : {uri!r}")
    fragment = uri.split("#", 1)[1]
    match = _VERSION_RE.match(fragment)
    if not match:
        raise ValueError(f"Fragment de version invalide : {fragment!r}")
    return int(match.group(1))


def base_uri(uri: str) -> str:
    """Retourne l'URI de lignée (sans fragment #version)."""
    return uri.split("#")[0]


def increment_version(uri: str) -> str:
    """Retourne un URI avec la version incrémentée d'une unité."""
    current = extract_version(uri)
    return f"{base_uri(uri)}#v{current + 1}"


def is_valid_uri(uri: str) -> bool:
    """Vérifie qu'un URI respecte le format attendu."""
    try:
        extract_uuid(uri)
        extract_version(uri)
        return True
    except ValueError:
        return False


def short_id(uri: str) -> str:
    """Retourne les 8 premiers caractères de l'UUID pour affichage visuel."""
    return extract_uuid(uri)[:8]
