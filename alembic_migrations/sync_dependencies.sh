#!/usr/bin/env bash
set -Eeuo pipefail

PYPROJECT="pyproject.toml"
IN_DOCKER="${RUNNING_INSIDE_DOCKER:-0}"


uv_sync() {
  if [[ "$IN_DOCKER" == "1" ]]; then
    uv sync
  else
    # First try quiet; if fails, print output.
    if ! uv sync --extra dev >/dev/null 2>&1; then
      uv sync --extra dev
    fi
  fi
}


main() {
  # Create a pristine backup to guarantee full restore of the file afterwards
  local backup
  backup="$(mktemp)"
  cp "$PYPROJECT" "$backup"

  # Ensure we always restore the original file on error
  trap 'cp "$backup" "$PYPROJECT"; rm -f "$backup"' EXIT

  echo "🔎 Detecting git-based dependencies in $PYPROJECT …"
  # Comment out ALL dependencies that look like "name @ git+…"
  # Matches lines like:   "pkg @ git+https://repo/url.git",   (with optional trailing comma/space)
  echo "🚫 Disabling git deps…"
  sed -i -E 's|^([[:space:]]*"[[:alnum:]_.-]+[[:space:]]+@+[[:space:]]+git\+[^"#]+",?[[:space:]]*)$|# \1|' "$PYPROJECT"

  uv_sync

  echo "✅ Re-enabling git deps…"
  # Uncomment back those lines we just commented
  sed -i -E 's|^#[[:space:]]*([[:space:]]*"[[:alnum:]_.-]+[[:space:]]+@+[[:space:]]+git\+[^"#]+",?[[:space:]]*)$|\1|' "$PYPROJECT"

  uv_sync

  # Restore original file to be extra-safe (even if sed round-trip matched perfectly)
  cp "$backup" "$PYPROJECT"
  rm -f "$backup"
  trap - EXIT

  echo "♻️  All git dependencies have been reloaded."
}


main "$@"