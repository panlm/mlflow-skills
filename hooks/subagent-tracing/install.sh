#!/bin/bash
# Install SubagentStop tracing patch for MLflow claude_code module.
# Copies patched cli.py, hooks.py, tracing.py over the installed MLflow package.
#
# Usage:
#   bash hooks/subagent-tracing/install.sh
#
# To uninstall (restore originals), reinstall mlflow:
#   pip install mlflow==3.11.1

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Locate installed MLflow claude_code directory
TARGET=$(python3 -c "import mlflow, os; print(os.path.join(os.path.dirname(mlflow.__file__), 'claude_code'))")

if [ ! -d "$TARGET" ]; then
    echo "ERROR: mlflow.claude_code not found at $TARGET"
    exit 1
fi

echo "Patching mlflow.claude_code at: $TARGET"

for f in cli.py hooks.py tracing.py; do
    if [ ! -f "$TARGET/$f.orig" ]; then
        cp "$TARGET/$f" "$TARGET/$f.orig"
        echo "  Backed up $f -> $f.orig"
    fi
    cp "$SCRIPT_DIR/$f" "$TARGET/$f"
    echo "  Installed $f"
done

echo ""
echo "Done. SubagentStop tracing is now available."
echo "Run 'mlflow autolog claude' in your project to register the new hooks."
echo ""
echo "To uninstall: pip install --force-reinstall mlflow==$(python3 -c 'import mlflow; print(mlflow.__version__)')"
