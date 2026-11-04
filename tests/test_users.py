import json

import pytest

from app.auth import ConfigError, hash_password, load_users


def _write(path, users):
    path.write_text(json.dumps({"users": users}), encoding="utf-8")


def test_loads_known_user_and_hides_unknown(tmp_path):
    path = tmp_path / "users.json"
    _write(
        path,
        [
            {
                "username": "admin",
                "role": "admin",
                "password_hash": hash_password("MonitorDemo#1"),
            }
        ],
    )

    users = load_users(path)

    assert users["admin"]["role"] == "admin"
    assert "viewer" not in users


def test_rejects_plaintext_password_field(tmp_path):
    path = tmp_path / "users.json"
    _write(
        path,
        [
            {
                "username": "admin",
                "role": "admin",
                "password": "MonitorDemo#1",
                "password_hash": hash_password("MonitorDemo#1"),
            }
        ],
    )

    with pytest.raises(ConfigError, match="plaintext password"):
        load_users(path)
