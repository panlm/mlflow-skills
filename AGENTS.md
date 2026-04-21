# Skill Evaluation with MLflow

## Quick Start

```bash
# 1. Set up environment
source .env          # needs OPENAI_API_KEY and OPENAI_BASE_URL

# 2. Run evaluation
python tests/test_skill.py tests/configs/aws_best_practice_research.yaml
```

## How It Works

1. Test runner starts MLflow server, installs skill into a temp project
2. Runs Claude Code headless (`claude -p`) with the configured prompt
3. MLflow captures all tool calls as a trace
4. LLM judges read the trace and score yes/no on each check

## File Structure

```
tests/
  test_skill.py                         # Main test runner
  config.py                             # YAML config parser and data classes
  infra.py                              # Infrastructure: MLflow server, skill install, etc.
  utils.py                              # Shared utilities
  run_judges.py                         # Subprocess entry point for running judges
  configs/
    aws_best_practice_research.yaml     # Checklist-only test (10 judges)
    aws_best_practice_assessment.yaml   # Live assessment test (12 judges)
  judges/
    llm_judges.py                       # Generic judge - reads definitions from YAML
  scripts/
    setup_aws_bp_research.py            # Creates project dir, copies .mcp.json
```

## Adding a New Skill Evaluation

Only need one YAML file. Copy an existing config and change:

- `skills` - which skill to test
- `prompt` - what to tell Claude Code
- `judge_definitions` - what to check (plain text questions)

Example judge definition:

```yaml
judge_definitions:
  - name: my-check
    question: >
      Check that the agent did X.
      Answer 'yes' if you see evidence in the trace.
```

`llm_judges.py` is reusable across all skills - no Python needed.

## Testing Skills from an External Repo

You can develop skills in a separate repo and run tests without copying
anything into the mlflow-skills repo. Use the `project_root` field in YAML.

### External repo structure

```
my-skills-repo/
├── skill-a/
│   ├── SKILL.md
│   └── references/
├── skill-b/
│   ├── SKILL.md
│   └── references/
├── tests/
│   ├── configs/
│   │   └── skill_a_test.yaml    # project_root: ../..
│   ├── scripts/                 # optional setup scripts
│   └── judges/                  # optional custom judges
└── .env
```

### Minimal external YAML config

```yaml
name: "skill-a-test"
project_dir: skill-a-workdir
project_root: ../..              # relative to this YAML file -> repo root

skills:
  - skill-a

# setup_script: omit to auto-create project dir
# judges: omit to auto-use framework's built-in llm_judges.py

prompt: "Do something with skill-a. Do not ask for input."
timeout_seconds: 900
allowed_tools: "Bash,Read,Write,Edit,Grep,Glob,WebFetch"

judge_definitions:
  - name: skill-invoked
    question: >
      Check that skill-a was loaded. Answer 'yes' if you see evidence.

environment:
  OPENAI_API_KEY: ""
  OPENAI_BASE_URL: ""
```

### Running from the external repo

```bash
cd my-skills-repo
source .env
python /path/to/mlflow-skills/tests/test_skill.py tests/configs/skill_a_test.yaml
```

### Path resolution rules

When `project_root` is set in YAML:

| Item | Resolved from |
|------|---------------|
| `skills` | `project_root / skill_name` |
| `setup_script` | `project_root / setup_script` |
| `judges` | `project_root / judge_path` |

When `project_root` is **not** set (backward compatible):

| Item | Resolved from |
|------|---------------|
| `skills` | `repo_root / skill_name` |
| `setup_script` | `repo_root / setup_script` |
| `judges` | `repo_root / judge_path` |

### Optional fields

- **`setup_script`** — if omitted, the framework just creates the project directory
- **`judges`** — if omitted but `judge_definitions` exist, the framework
  auto-uses the built-in `tests/judges/llm_judges.py`

## YAML Config Reference

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | yes | — | Test run name |
| `project_dir` | yes | — | Temp project directory name |
| `skills` | yes | — | List of skill directory names to install |
| `prompt` | yes | — | Prompt sent to Claude Code |
| `project_root` | no | repo root | Base directory for resolving skills, setup_script, judges (relative to YAML file) |
| `setup_script` | no | none | Setup script path (relative to project_root) |
| `judges` | no | auto | Judge module paths (relative to project_root); auto-uses built-in if omitted |
| `judge_definitions` | no | `[]` | List of `{name, question}` dicts for LLM judges |
| `timeout_seconds` | no | `900` | Claude Code execution timeout |
| `verification_timeout` | no | `300` | Judge verification timeout |
| `allowed_tools` | no | `Bash,Read,...` | Comma-separated tool allowlist for Claude Code |
| `mlflow_port` | no | `5000` | Local MLflow server port |
| `tracking_uri` | no | none | External MLflow/Databricks tracking URI |
| `test_runs_dir` | no | `/tmp` | Parent directory for temp work directories |
| `keep_workdir` | no | `true` | Keep work directory after test completes |
| `environment` | no | `{}` | Extra environment variables (empty values won't override existing) |

## Prerequisites

- Python venv with `mlflow[genai]>=3.8`, `openai`, `pyyaml`, `litellm`
- Claude Code CLI (`claude`) with headless mode (`-p`)
- `.env` with `OPENAI_API_KEY` and `OPENAI_BASE_URL` (for LLM judges)
- `.mcp.json` with MCP servers (for skills that need them)

## Notes

- `.env` and `.mcp.json` are in `.gitignore` - never committed
- YAML `environment` fields with empty values won't override existing env vars
- Each run creates a temp dir under `/tmp/` with logs and MLflow data
- MLflow UI is available during the run at `http://127.0.0.1:{mlflow_port}`
