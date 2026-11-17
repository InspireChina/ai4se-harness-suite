#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PATH="${HOME}/.opencode/bin:${PATH}"
echo "项目: $ROOT"
echo "队列: default"
./.overnight-runner/overnight-runner list
echo
echo "启动 attended 前台面板（左队列 / 右 agent）。按 q 退出。"
exec ./.overnight-runner/overnight-runner run --mode attended
