"""
Ed25519 proof-of-work signing via PyNaCl.

Canonical payload bytes are SHA-256 hashed; the hash hex is stored alongside
the base64-encoded detached signature.
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from django.conf import settings
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey


class SigningError(Exception):
    pass


class VerificationError(Exception):
    pass


def canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def payload_hash(message: bytes) -> str:
    return hashlib.sha256(message).hexdigest()


def _signing_key() -> SigningKey:
    key_b64 = getattr(settings, "POW_SIGNING_PRIVATE_KEY", "")
    if key_b64:
        raw = base64.b64decode(key_b64)
        if len(raw) != 32:
            raise SigningError("POW_SIGNING_PRIVATE_KEY must decode to 32 bytes.")
        return SigningKey(raw)
    seed = hashlib.sha256(
        f"pow-signing:{settings.SECRET_KEY}".encode("utf-8")
    ).digest()
    return SigningKey(seed)


def public_key_b64() -> str:
    stored = getattr(settings, "POW_SIGNING_PUBLIC_KEY", "")
    if stored:
        return stored
    return base64.b64encode(bytes(_signing_key().verify_key)).decode("ascii")


def sign_payload(payload: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    """
    Sign a proof-of-work payload.

    Returns (signature_hash, signature_b64, payload).
    """
    message = canonical_json(payload)
    signed = _signing_key().sign(message)
    sig_hash = payload_hash(message)
    sig_b64 = base64.b64encode(signed.signature).decode("ascii")
    return sig_hash, sig_b64, payload


def verify_signature(
    payload: dict[str, Any],
    signature_b64: str,
    *,
    public_key_b64_override: str | None = None,
) -> bool:
    message = canonical_json(payload)
    key_b64 = public_key_b64_override or public_key_b64()
    verify_key = VerifyKey(base64.b64decode(key_b64))
    signature = base64.b64decode(signature_b64)
    try:
        verify_key.verify(message, signature)
        return True
    except BadSignatureError:
        return False


def verify_reference(
    payload: dict[str, Any],
    signature_b64: str,
    expected_hash: str,
) -> dict[str, Any]:
    message = canonical_json(payload)
    computed_hash = payload_hash(message)
    if computed_hash != expected_hash:
        raise VerificationError("Payload hash mismatch.")

    if not verify_signature(payload, signature_b64):
        raise VerificationError("Ed25519 signature invalid.")

    return {
        "valid": True,
        "payload_hash": computed_hash,
        "payload": payload,
        "public_key": public_key_b64(),
    }
