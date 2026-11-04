"""Demo monitoring application."""

import os
from datetime import timedelta
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from app.auth import LOGIN_FAILURE_MESSAGE, credentials_match, load_users

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "monitoring.json"


def create_app(config_path=None):
    secret = os.environ.get("FLASK_SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "FLASK_SECRET_KEY is required and must be set in the environment."
        )

    users = load_users(config_path or DEFAULT_CONFIG_PATH)
    app = Flask(__name__)
    app.secret_key = secret
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    @app.get("/")
    def index():
        if "username" not in session:
            return redirect(url_for("login"))
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if credentials_match(users.get(username), password):
                user = users[username]
                session.clear()
                session["username"] = user["username"]
                session["role"] = user["role"]
                session.permanent = True
                return redirect(url_for("index"))
            app.logger.warning(
                "sign-in failed username=%s result=rejected",
                username.replace("\r", "").replace("\n", ""),
            )
            error = LOGIN_FAILURE_MESSAGE
        return render_template("login.html", error=error)

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    return app
