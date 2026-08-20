#!/usr/bin/env bash
# PostToolUse(Edit|Write): compile the enclosing project's main .tex and feed
# errors straight back to Claude (exit 2). This IS the LaTeX feedback loop —
# without it broken markup is only discovered 20 edits later.
#
# ponytail: no debounce, no incremental build. If it gets slow on a long paper,
# delete the hook entry in .claude/settings.json and compile by hand instead.
set -u

command -v tectonic >/dev/null 2>&1 || exit 0

file=$(jq -r '.tool_input.file_path // empty')
case "$file" in *.tex) ;; *) exit 0 ;; esac

dir=$(dirname "$file")
main=""
for c in main.tex paper.tex slides.tex; do
  [ -f "$dir/$c" ] && main=$c && break
done
[ -n "$main" ] || exit 0   # a fragment in a subdir; its parent build will catch it

out=$(cd "$dir" && tectonic "$main" 2>&1) && exit 0

{
  echo "LaTeX build failed: $dir/$main"
  printf '%s\n' "$out" | grep -iE '^(error|warning: error|!|.*\.tex:[0-9]+)' | head -20
} >&2
exit 2
