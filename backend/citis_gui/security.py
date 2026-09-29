from __future__ import annotations
import base64, os, secrets
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.fernet import Fernet

_ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2, hash_len=32)

KDF_TIME = 3
KDF_MEM = 65536
KDF_PAR = 2


def hash_master(password: str) -> str:
    return _ph.hash(password)


def verify_master(password: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, password)
    except Exception:
        return False


def derive_vault_key(password: str, salt: bytes) -> bytes:
    raw = hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=KDF_TIME,
        memory_cost=KDF_MEM,
        parallelism=KDF_PAR,
        hash_len=32,
        type=Type.ID,
    )
    return base64.urlsafe_b64encode(raw)


def new_salt() -> bytes:
    return os.urandom(16)


def encrypt(key: bytes, plaintext: str) -> bytes:
    return Fernet(key).encrypt(plaintext.encode())


def decrypt(key: bytes, blob: bytes) -> str:
    return Fernet(key).decrypt(blob).decode()


def new_token() -> str:
    return secrets.token_urlsafe(32)