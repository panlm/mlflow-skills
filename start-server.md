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

## 3. Run Judges on Collected Traces

Use the test framework's `run_judges.py` to evaluate traces against YAML-defined judges.

### Prerequisites

```bash
source .env   # sets OPENAI_API_KEY and OPENAI_BASE_URL
source .venv/bin/activate
```

### Run

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_EXPERIMENT_ID=0
export CC_EXPERIMENT_ID=0
export RUN_START_MS=0  # 0 = evaluate all traces; or set to epoch ms to filter

# Load judge definitions from YAML config (filtered by test_scope)
export JUDGE_DEFINITIONS=$(python3 -c "
import yaml, json
with open('<path-to-yaml-config>') as f:
    config = yaml.safe_load(f)
scope = config.get('test_scope', 'all')
judges = [j for j in config['judge_definitions'] if j.get('scope','all') in ('all', scope)]
print(json.dumps(judges))
")

export JUDGE_PATHS='["/home/ubuntu/mlflow-skills/tests/judges/llm_judges.py"]'

python tests/run_judges.py
```

Replace `<path-to-yaml-config>` with the actual config path, e.g.:
```
/home/ubuntu/skills/tests/configs/aws-best-practice-research.yaml
```

### Parameters

| Env Var | Description |
|---------|-------------|
| `CC_EXPERIMENT_ID` | Experiment containing the traces to evaluate |
| `MLFLOW_EXPERIMENT_ID` | Fallback experiment if CC experiment has no traces |
| `RUN_START_MS` | Only evaluate traces created after this timestamp (ms); `0` = all |
| `SESSION_ID` | (Optional) Only evaluate traces from this session |
| `JUDGE_DEFINITIONS` | JSON array of judge objects (name, scope, question) |
| `JUDGE_PATHS` | JSON array of paths to Python modules exposing `get_judges()` |
| `JUDGE_MODEL` | LLM model for judging (default: `opus-4-6`) |

### Output

JSON array printed to stdout:

```json
[
  {
    "scorer": "skill-invoked",
    "trace_id": "tr-xxx",
    "value": "yes",
    "rationale": "...",
    "pass": true
  }
]
```

Results are also logged to MLflow as an evaluation run — view at:
```
http://localhost:5000/#/experiments/<id>/evaluation-runs
```

### Evaluate a Specific Session

List sessions and their trace counts:

```bash
python3 -c "
import mlflow
mlflow.set_tracking_uri('http://localhost:5000')
df = mlflow.search_traces(experiment_ids=['0'])
sessions = df['trace_metadata'].apply(lambda m: m.get('mlflow.trace.session','unknown'))
for sid, count in sessions.value_counts().items():
    print(f'{sid}  ({count} traces)')
"
```

Then pass `SESSION_ID` to evaluate only that session:

```bash
export SESSION_ID="cab7174a-74fa-46db-ac7e-2a8668ff6202"
export RUN_START_MS=0
python tests/run_judges.py
```

### Evaluate a Single Trace

Set `RUN_START_MS` to just before the target trace's timestamp:

```bash
# Find trace timestamp
python3 -c "
import mlflow
mlflow.set_tracking_uri('http://localhost:5000')
df = mlflow.search_traces(experiment_ids=['0'])
print(df[['trace_id','request_time']].to_string())
"

# Set RUN_START_MS to 1ms before target trace
export RUN_START_MS=<timestamp_ms - 1>
python tests/run_judges.py
```
