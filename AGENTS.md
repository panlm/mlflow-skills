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
  configs/
    aws_best_practice_research.yaml   # Checklist-only test (10 judges)
    aws_best_practice_assessment.yaml # Live assessment test (12 judges)
  judges/
    llm_judges.py                     # Generic judge - reads definitions from YAML
  scripts/
    setup_aws_bp_research.py          # Creates project dir, copies .mcp.json
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

## Prerequisites

- Python venv at `/home/ubuntu/venv` with `mlflow[genai]>=3.8`, `openai`, `pyyaml`, `litellm`
- Claude Code CLI (`claude`) with headless mode (`-p`)
- `.env` with `OPENAI_API_KEY` and `OPENAI_BASE_URL` (for LLM judges)
- `.mcp.json` with MCP servers (for skills that need them)

## Notes

- `.env` and `.mcp.json` are in `.gitignore` - never committed
- YAML `environment` fields with empty values won't override existing env vars
- Each run creates a temp dir under `/tmp/` with logs and MLflow data
- MLflow UI is available during the run at `http://127.0.0.1:{mlflow_port}`
