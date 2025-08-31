#!/usr/bin/env bash
set -euo pipefail

MODE="${MODE:-fix}"

ESLINT_CFG="config/eslint.mjs"
STYLELINT_CFG="config/stylelint.cjs"
PRETTIER_CFG="config/prettier.json"

PRETTIER_PATTERNS=(
  "**/*.{html,css,scss}"
  "**/*.{js,jsx,mjs,cjs}"
  "**/*.{ts,tsx,mts,cts}"
  "**/*.{json,md}"
)

STYLELINT_PATTERNS=( "**/*.{css,scss,html}" )
ESLINT_EXTS=".js,.mjs,.cjs,.jsx,.html"


run_step() {
  local title="$1"; shift
  echo "▶ ${title}"
  "$@"
  echo
}


prettier_cmd() {
  local action=()
  if [[ "$MODE" == "fix" ]]; then
    action=(--write)
  else
    action=(--check)
  fi

  npx prettier \
    "${action[@]}" \
    --config "$PRETTIER_CFG" \
    --ignore-path .gitignore \
    --no-error-on-unmatched-pattern \
    "${PRETTIER_PATTERNS[@]}"
}


stylelint_cmd() {
  local maybe_fix=()
  if [[ "$MODE" == "fix" ]]; then
    maybe_fix=(--fix)
  fi

  npx stylelint \
    "${STYLELINT_PATTERNS[@]}" \
    "${maybe_fix[@]}" \
    --allow-empty-input \
    --config "$STYLELINT_CFG"
}


eslint_cmd() {
  local maybe_fix=()
  if [[ "$MODE" == "fix" ]]; then
    maybe_fix=(--fix)
  fi

  npx eslint \
    . \
    --ext "$ESLINT_EXTS" \
    "${maybe_fix[@]}" \
    --config "$ESLINT_CFG"
}


main() {
  run_step "Prettier (${MODE})"      prettier_cmd
  run_step "Stylelint (${MODE})"     stylelint_cmd
  run_step "ESLint (${MODE})"        eslint_cmd

  if [[ -f scripts/enforce-blank-lines.mjs ]]; then
    run_step "Enforce 2 blank lines (HTML/CSS/JS)" node scripts/enforce-blank-lines.mjs
  fi

  echo "✅ Done (${MODE})"
}

main "$@"


