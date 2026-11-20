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

# ── 安装清单 ────────────────────────────────────────────────────────
# 一个模块一个文件，谁安装谁写自己那份：不需要合并，也不需要跨模块共享列表。
MANIFEST_MODULE="agents-workflow-engine"
MANIFEST_DIR="$PROJECT/.agents/harness"
MANIFEST_FILE="$MANIFEST_DIR/$MANIFEST_MODULE.json"
SUITE_VERSION="$(sed -n '1s/[[:space:]]*$//;1p' "$ROOT/../VERSION" 2>/dev/null || true)"

# 从清单里取字段值：{ "version": "0.2.0", ... }
manifest_field() {
  sed -n "s/.*\"$2\": *\"\([^\"]*\)\".*/\1/p" "$1" 2>/dev/null | head -1
}

# 已装版本没变就不动文件（installedAt 保持首次安装时间）；变了自己又没 --force 就不许改清单
write_manifest() {
  if [ -z "$VERSION" ]; then
    echo "  清单: 读不到本仓库的引擎版本，跳过" >&2
    return 0
  fi
  if [ -f "$MANIFEST_FILE" ]; then
    old_version="$(manifest_field "$MANIFEST_FILE" version)"
    old_suite="$(manifest_field "$MANIFEST_FILE" suite)"
    if [ "$old_version" = "$VERSION" ] && [ "$old_suite" = "$SUITE_VERSION" ]; then
      echo "  [清单] ${MANIFEST_MODULE} ${VERSION}（未变）"
      return 0
    fi
    if [ "$FORCE" -eq 0 ]; then
      echo "  清单: ${MANIFEST_FILE} 记着 ${MANIFEST_MODULE} ${old_version:-未知}（套件 ${old_suite:-未知}），本次源码是 ${VERSION}（套件 ${SUITE_VERSION}）；清单未改，要升级加 --force" >&2
      return 0
    fi
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 写清单 ${MANIFEST_FILE}（${MANIFEST_MODULE} ${VERSION} / 套件 ${SUITE_VERSION}）"
    return 0
  fi
  mkdir -p "$MANIFEST_DIR"
  tmp="$MANIFEST_FILE.tmp.$$"
  {
    printf '{\n'
    printf '  "module": "%s",\n' "$MANIFEST_MODULE"
    printf '  "version": "%s",\n' "$VERSION"
    printf '  "suite": "%s",\n' "$SUITE_VERSION"
    printf '  "installedAt": "%s"\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '}\n'
  } > "$tmp"
  mv "$tmp" "$MANIFEST_FILE"
  echo "  [清单] ${MANIFEST_MODULE} ${VERSION}（套件 ${SUITE_VERSION}）→ ${MANIFEST_FILE}"
}

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
  write_manifest
  exit 0
fi

mkdir -p "$DEST"
if [ -f "$FILE" ] && [ "$FORCE" -eq 0 ]; then
  echo "  跳过: 已存在 $FILE"
  echo "  清单没动：文件没升级，清单也不应该升级（要升级加 --force）"
  exit 0
fi
tmp="$FILE.tmp.$$"
cp "$PRESET" "$tmp"
mv "$tmp" "$FILE"
echo "  已写入 $FILE"
echo "  未修改 overlay.yaml"
write_manifest
