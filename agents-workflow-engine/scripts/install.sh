#!/usr/bin/env bash
# 把工作流预设安装到目标项目的 .agents/workflow/preset.yaml。
# 不覆盖已有 overlay.yaml。
#
# 用法：
#   ./install.sh <目标项目目录> [--dry-run] [--force]
#
#   --dry-run  只打印将要写的文件
#   --force    覆盖已有 preset.yaml

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRESET="$ROOT/presets/iteration-to-test.yaml"
VERSION="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' "$ROOT/agents_workflow_engine/version.py" 2>/dev/null || true)"
DRY_RUN=0
FORCE=0
TARGET=""

usage() {
  sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --force) FORCE=1 ;;
    -h|--help) usage 0 ;;
    -*) echo "未知参数: $1" >&2; usage 1 ;;
    *) TARGET="$1" ;;
  esac
  shift
done

if [ -z "$TARGET" ]; then
  echo "错误：缺少目标项目目录。" >&2
  usage 1
fi
if [ ! -d "$TARGET" ]; then
  echo "错误：目标目录不存在: $TARGET" >&2
  exit 1
fi

PROJECT="$(cd "$TARGET" && pwd)"
DEST="$PROJECT/.agents/workflow"
FILE="$DEST/preset.yaml"

if [ -n "$VERSION" ]; then
  echo "agents-workflow-engine 安装器（引擎 ${VERSION}）"
else
  echo "agents-workflow-engine 安装器"
fi
echo "  预设: $PRESET"
echo "  目标: $FILE"

# 预设与引擎要成对升级：项目里装了引擎就对比一下版本，不对就提醒。
INSTALLED="$PROJECT/.agents/workflow/engine/agents_workflow_engine/version.py"
HAVE=""
if [ -f "$INSTALLED" ]; then
  HAVE="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' "$INSTALLED" 2>/dev/null || true)"
  if [ -n "$HAVE" ] && [ "$HAVE" = "$VERSION" ]; then
    echo "  引擎: 项目里是 ${HAVE}，与本预设一致"
  else
    echo "  引擎: 项目里是 ${HAVE:-未知}，本预设要 ${VERSION} —— 不一致，别只装预设" >&2
  fi
else
  echo "  引擎: 项目里没有 .agents/workflow/engine（或 0.1.x，没有 version.py），预设的图级 models 会被忽略" >&2
fi

if [ "$DRY_RUN" -eq 1 ]; then
  if [ -f "$FILE" ] && [ "$FORCE" -eq 0 ]; then
    echo "  跳过: 已存在 preset.yaml（没有 --force）"
  else
    echo "  将写入 preset.yaml"
  fi
  echo "  不碰 overlay.yaml"
  exit 0
fi

mkdir -p "$DEST"
if [ -f "$FILE" ] && [ "$FORCE" -eq 0 ]; then
  echo "  跳过: 已存在 $FILE"
  exit 0
fi
tmp="$FILE.tmp.$$"
cp "$PRESET" "$tmp"
mv "$tmp" "$FILE"
echo "  已写入 $FILE"
echo "  未修改 overlay.yaml"
