# SubagentStop Tracing for MLflow Claude Code

Adds native `SubagentStop` hook support to MLflow's Claude Code integration, so subagent conversations are traced independently with proper session isolation.

## What it does

- Registers a `SubagentStop` hook alongside the existing `Stop` hook when running `mlflow autolog claude`
- Adds `mlflow autolog claude subagent-stop-hook` CLI command
- Subagent traces get their own session ID: `{parent_session}::subagent-{type}-{id}`
- Parent session ID is stored in `mlflow.claude_code_parent_session` metadata for correlation
- Agent type/ID stored in `mlflow.claude_code_agent_type` / `mlflow.claude_code_agent_id`

## Install

```bash
bash hooks/subagent-tracing/install.sh
```

Then re-run setup in your project directory:

```bash
mlflow autolog claude
```

## Uninstall

```bash
pip install --force-reinstall mlflow==3.11.1
```

## Files modified

| File | Changes |
|------|---------|
| `cli.py` | Added `subagent-stop-hook` subcommand |
| `hooks.py` | `setup_hooks_config()` registers `SubagentStop`; added `subagent_stop_hook_handler()` |
| `tracing.py` | `process_transcript()` accepts `agent_id`/`agent_type`; subagent session isolation; new metadata keys |
