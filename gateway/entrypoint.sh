#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="src"
CHECK_PATH="${CHECK_PATH:-$PROJECT_ROOT}"

# - ANN* — absence/incorrect type hints (flake8-annotations)
# - TCH* — proper placement of imports for type checking (flake8-type-checking)
RUFF_RULES="${RUFF_RULES:-ANN,TCH}"
RUFF_IGNORES="${RUFF_IGNORES:-ANN401}"
RUFF_FIX="${RUFF_FIX:-0}"

SYNC_CMD="${SYNC_CMD:-./sync_dependencies.sh}"
APP_CMD="${APP_CMD:-uv run main.py}"


if [[ "${RUNNING_INSIDE_DOCKER:-0}" != "1" ]]; then
  echo "📦 Installing dev dependencies (extras)…"
  uv sync --extra dev >/dev/null

  echo "🔎 Ruff (rules: $RUFF_RULES; ignore: ${RUFF_IGNORES:-<none>})…"
  ruff_args=(check "$CHECK_PATH" --select "$RUFF_RULES")
  [[ -n "${RUFF_IGNORES// }" ]] && ruff_args+=(--ignore "$RUFF_IGNORES")
  [[ "$RUFF_FIX" == "1" ]] && ruff_args+=(--fix)
  uv run ruff "${ruff_args[@]}"

  echo "🔬 Mypy (strict)…"
  uv run mypy "$CHECK_PATH"
else
  echo "🐳 RUNNING_INSIDE_DOCKER=1 → skipping Ruff & Mypy."
fi


if [[ -n "${SYNC_CMD// }" ]]; then
  echo "🔁 Running sync step: $SYNC_CMD"
  if [[ -f "$SYNC_CMD" ]]; then
    chmod +x "$SYNC_CMD"
    "$SYNC_CMD"
  else
    bash -lc "$SYNC_CMD"
  fi
fi


exec $APP_CMD