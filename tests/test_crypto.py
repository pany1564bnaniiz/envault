"""Unit tests for envault.crypto encryption/decryption utilities."""

import pytest
from cryptography.exceptions import InvalidTag

from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-password"
PLAINTEXT = "DATABASE_URL=postgres://localhost/mydb\nSECRET_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_decrypt_roundtrip():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    decoded = decrypt(encoded, PASSWORD)
    assert decoded == PLAINTEXT


def test_encrypt_produces_different_ciphertexts():
    """Each encryption should be unique due to random salt and nonce."""
    enc1 = encrypt(PLAINTEXT, PASSWORD)
    enc2 = encrypt(PLAINTEXT, PASSWORD)
    assert enc1 != enc2


def test_decrypt_wrong_password_raises():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(Exception):
        decrypt(encoded, "wrong-password")


def test_decrypt_tampered_data_raises():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    tampered = encoded[:-4] + "XXXX"
    with pytest.raises(Exception):
        decrypt(tampered, PASSWORD)


def test_encrypt_empty_string():
    encoded = encrypt("", PASSWORD)
    decoded = decrypt(encoded, PASSWORD)
    assert decoded == ""
