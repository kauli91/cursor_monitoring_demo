import pytest


def test_create_app_imports():
    from app import create_app

    assert callable(create_app)


def test_missing_secret_does_not_read_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("FLASK_SECRET_KEY", raising=False)
    (tmp_path / ".env").write_text(
        "FLASK_SECRET_KEY=from-developer-dotenv\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    from app import create_app

    with pytest.raises(RuntimeError) as exc:
        create_app()

    message = str(exc.value)
    assert "FLASK_SECRET_KEY" in message
    assert "from-developer-dotenv" not in message
