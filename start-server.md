# MLflow Tracing Server

## 1. Start Server

```bash
source .venv/bin/activate

python -m mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 1 \
  --backend-store-uri "sqlite:///mlflow-data/mlflow.db" \
  --default-artifact-root mlflow-data/artifacts \
  --allowed-hosts "*" \
  --cors-allowed-origins "*"
```

Run from the repo root directory.

Key flags:
- `--host 0.0.0.0` + `--allowed-hosts "*"` — allow access from any host (not just localhost)
- `--cors-allowed-origins "*"` — allow cross-origin requests
- `--workers 1` — single worker to avoid child process issues with SQLite

UI: `http://<server-ip>:5000`

## 2. Send Claude Code Traces to Server

```bash
source .venv/bin/activate

mlflow autolog claude \
  -d <project-dir> \
  -u http://<server-ip>:5000
```

- `-d` — Claude Code project directory (e.g. `~/git/panlm-skills`)
- `-u` — MLflow tracking URI; use actual IP if Claude Code is on a different machine
- Traces are sent to the default experiment (ID `0`); use `-e <id>` or `-n <name>` to specify a different one

This writes a Stop hook into `<project-dir>/.claude/settings.json`. After each Claude Code session ends, the transcript is automatically converted into an MLflow trace and sent to the server.

### Check / Disable

```bash
mlflow autolog claude --status  -d <project-dir>   # check current status
mlflow autolog claude --disable -d <project-dir>   # disable tracing
```
