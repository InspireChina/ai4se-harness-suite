#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
export PATH="${HOME}/.opencode/bin:${PATH}"
echo "=== overnight-runner (attended) ==="
./.overnight-runner/overnight-runner list
echo
exec ./.overnight-runner/overnight-runner run --mode attended
