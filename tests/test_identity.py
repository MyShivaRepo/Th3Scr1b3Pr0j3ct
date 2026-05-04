"""Tests unitaires — couche 1 : identité."""

import pytest

from src.model.identity import (
    base_uri,
    extract_uuid,
    extract_version,
    generate_uri,
    increment_version,
    is_valid_uri,
    short_id,
)

URN_PREFIX = "urn:concept:scribe:"


def test_generate_uri_format():
    uri = generate_uri()
    assert uri.startswith(URN_PREFIX)
    assert "#v1" in uri


def test_generate_uri_uniqueness():
    uris = {generate_uri() for _ in range(100)}
    assert len(uris) == 100


def test_extract_uuid():
    uri = f"{URN_PREFIX}AABBCCDD-1234-1234-1234-AABBCCDDEEFF#v1"
    assert extract_uuid(uri) == "AABBCCDD-1234-1234-1234-AABBCCDDEEFF"


def test_extract_uuid_invalid_prefix():
    with pytest.raises(ValueError):
        extract_uuid("urn:invalid:scribe:ABC#v1")


def test_extract_version():
    assert extract_version(f"{URN_PREFIX}AABB#v1") == 1
    assert extract_version(f"{URN_PREFIX}AABB#v42") == 42


def test_extract_version_no_fragment():
    with pytest.raises(ValueError):
        extract_version(f"{URN_PREFIX}AABB")


def test_extract_version_invalid_fragment():
    with pytest.raises(ValueError):
        extract_version(f"{URN_PREFIX}AABB#latest")


def test_base_uri():
    uri = f"{URN_PREFIX}AABB#v3"
    assert base_uri(uri) == f"{URN_PREFIX}AABB"


def test_increment_version():
    uri = f"{URN_PREFIX}AABB#v1"
    assert increment_version(uri) == f"{URN_PREFIX}AABB#v2"
    assert increment_version(increment_version(uri)) == f"{URN_PREFIX}AABB#v3"


def test_is_valid_uri_true():
    uri = generate_uri()
    assert is_valid_uri(uri) is True


def test_is_valid_uri_false():
    assert is_valid_uri("not-a-valid-uri") is False
    assert is_valid_uri(f"{URN_PREFIX}AABB") is False


def test_short_id():
    uri = f"{URN_PREFIX}AABBCCDD-1234-1234-1234-AABBCCDDEEFF#v1"
    assert short_id(uri) == "AABBCCDD"
