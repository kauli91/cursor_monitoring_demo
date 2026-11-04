# Demo Monitoring

Demo monitoring for Linux servers. The app shows simulated CPU, memory, disk, load average, and uptime so internal teams can check host health without a shell login.

The product specification is in [docs/requirements.md](docs/requirements.md).

## Install

```bash
python -m venv .venv
pip install -r requirements.txt
```

`requirements.txt` pins Flask to 3.1.3, so a later install stays on that reviewed release. Werkzeug is installed with Flask and is not listed separately. The `.venv/` directory stays off the branch.
