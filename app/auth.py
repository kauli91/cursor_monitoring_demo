"""Password hashes and the user list used by sign-in."""

import json
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

HASH_METHOD = "pbkdf2:sha256"
LOGIN_FAILURE_MESSAGE = "Invalid username or password."
_DUMMY_HASH = generate_password_hash("dummy-password", method=HASH_METHOD)


class ConfigError(Exception):
    """The user config cannot be loaded safely."""


def hash_password(password):
    return generate_password_hash(password, method=HASH_METHOD)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def credentials_match(user, password):
    """Check a password without treating a missing user as a different error."""
    stored = user["password_hash"] if user else _DUMMY_HASH
    matched = check_password_hash(stored, password)
    return user is not None and matched


def load_users(path):
    """Load admin and viewer accounts. Plaintext password fields are rejected."""
    config_path = Path(path)
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"could not read user config: {config_path}") from exc

    records = data.get("users") if isinstance(data, dict) else None
    if not isinstance(records, list):
        raise ConfigError(f"user config must contain a users list: {config_path}")

    users = {}
    for record in records:
        if not isinstance(record, dict):
            raise ConfigError("user record must be an object")
        if "password" in record:
            raise ConfigError("user record must not include a plaintext password")
        username = record.get("username")
        role = record.get("role")
        password_hash = record.get("password_hash")
        if not username or not password_hash:
            raise ConfigError("user record requires username and password_hash")
        if role not in {"admin", "viewer"}:
            raise ConfigError("user role must be admin or viewer")
        if not str(password_hash).startswith("pbkdf2:sha256"):
            raise ConfigError("password_hash must be a pbkdf2:sha256 hash")
        if username in users:
            raise ConfigError("duplicate username in user config")
        users[username] = {
            "username": username,
            "role": role,
            "password_hash": password_hash,
        }
    return users
