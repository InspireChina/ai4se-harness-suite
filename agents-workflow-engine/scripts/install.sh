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

echo "agents-workflow-engine 安装器"
echo "  预设: $PRESET"
echo "  目标: $FILE"

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
