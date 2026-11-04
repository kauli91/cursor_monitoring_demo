import logging

from app.auth import hash_password, verify_password

DEMO_PASSWORD = "MonitorDemo#1"


def test_hash_verifies_and_uses_pbkdf2():
    hashed = hash_password(DEMO_PASSWORD)

    assert hashed.startswith("pbkdf2:sha256")
    assert DEMO_PASSWORD not in hashed
    assert verify_password(hashed, DEMO_PASSWORD)
    assert not verify_password(hashed, "different-password")


def test_helpers_do_not_log_password_or_hash():
    records = []

    class ListHandler(logging.Handler):
        def emit(self, record):
            records.append(record)

    handler = ListHandler(level=logging.DEBUG)
    root = logging.getLogger()
    previous = root.level
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    try:
        hashed = hash_password(DEMO_PASSWORD)
        assert verify_password(hashed, DEMO_PASSWORD)
    finally:
        root.removeHandler(handler)
        root.setLevel(previous)

    rendered = " ".join(record.getMessage() for record in records)
    assert DEMO_PASSWORD not in rendered
    assert "pbkdf2" not in rendered
