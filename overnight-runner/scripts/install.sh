#!/usr/bin/env bash
# 把 overnight-runner 安装到目标项目的 `.overnight-runner/`。
#
# 用法：
#   ./install.sh <目标项目目录> [--dry-run] [--force] [--no-config] [--manifest-only]
#
#   --dry-run        只打印将要发生的改动，不写文件
#   --force          覆盖已存在的 runner 代码与启动脚本（不碰 queue / project.yaml）
#   --no-config      不创建 overnight-runner.yaml 与 project.yaml
#   --manifest-only  只更新 .agents/harness 清单（不装代码与配置）
#
# 零依赖：只用 Python 3.9+ 标准库，不需要 pip install。

set -euo pipefail

INSTALLER_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PKG_DIR="$INSTALLER_DIR/overnight_runner"
TARGET_DIR=".overnight-runner"
LEGACY_TOOLS="tools/overnight-runner"

DRY_RUN=0
FORCE=0
NO_CONFIG=0
MANIFEST_ONLY=0

usage() {
  sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)       DRY_RUN=1 ;;
    --force)         FORCE=1 ;;
    --no-config)     NO_CONFIG=1 ;;
    --manifest-only) MANIFEST_ONLY=1 ;;
    -h|--help)   usage 0 ;;
    -*)          echo "未知参数: $1" >&2; usage 1 ;;
    *)           TARGET="$1" ;;
  esac
  shift
done

if [ -z "${TARGET:-}" ]; then
  echo "错误：缺少目标项目目录。" >&2
  usage 1
fi
if [ ! -d "$TARGET" ]; then
  echo "错误：目标目录不存在: $TARGET" >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$TARGET" && pwd)"
DEST="$PROJECT_ROOT/$TARGET_DIR"
PKG_DEST="$DEST/overnight_runner"

# ── 安装清单 ────────────────────────────────────────────────────────
# 一个模块一个文件，谁安装谁写自己那份：不需要合并，也不需要跨模块共享列表。
MANIFEST_MODULE="overnight-runner"
MANIFEST_DIR="$PROJECT_ROOT/.agents/harness"
MANIFEST_FILE="$MANIFEST_DIR/$MANIFEST_MODULE.json"
SUITE_VERSION="$(sed -n '1s/[[:space:]]*$//;1p' "$INSTALLER_DIR/../VERSION" 2>/dev/null || true)"
MANIFEST_VERSION="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' "$PKG_DIR/__init__.py" 2>/dev/null || true)"
if [ -z "$SUITE_VERSION" ]; then
  echo "错误：读不到仓库根的 VERSION（$INSTALLER_DIR/../VERSION）" >&2
  exit 1
fi
if [ -z "$MANIFEST_VERSION" ]; then
  echo "错误：读不到 overnight_runner/__init__.py 里的 __version__" >&2
  exit 1
fi

# 从清单里取字段值：{ "version": "0.3.0", ... }
manifest_field() {
  sed -n "s/.*\"$2\": *\"\([^\"]*\)\".*/\1/p" "$1" 2>/dev/null | head -1
}

# 已装版本没变就不动文件（installedAt 保持首次安装时间）；变了自己又没 --force 就不许改清单
write_manifest() {
  if [ -f "$MANIFEST_FILE" ]; then
    old_version="$(manifest_field "$MANIFEST_FILE" version)"
    old_suite="$(manifest_field "$MANIFEST_FILE" suite)"
    if [ "$old_version" = "$MANIFEST_VERSION" ] && [ "$old_suite" = "$SUITE_VERSION" ]; then
      echo "  [清单] ${MANIFEST_MODULE} ${MANIFEST_VERSION}（未变）"
      return 0
    fi
    if [ "$FORCE" -eq 0 ] && [ "$MANIFEST_ONLY" -eq 0 ]; then
      echo "  清单: ${MANIFEST_FILE} 记着 ${MANIFEST_MODULE} ${old_version:-未知}（套件 ${old_suite:-未知}），本次源码是 ${MANIFEST_VERSION}（套件 ${SUITE_VERSION}）；文件是跳过模式，清单未改，要升级加 --force（代码已手工同步过就加 --manifest-only）" >&2
      return 0
    fi
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 写清单 ${MANIFEST_FILE}（${MANIFEST_MODULE} ${MANIFEST_VERSION} / 套件 ${SUITE_VERSION}）"
    return 0
  fi
  mkdir -p "$MANIFEST_DIR"
  tmp="$MANIFEST_FILE.tmp.$$"
  {
    printf '{\n'
    printf '  "module": "%s",\n' "$MANIFEST_MODULE"
    printf '  "version": "%s",\n' "$MANIFEST_VERSION"
    printf '  "suite": "%s",\n' "$SUITE_VERSION"
    printf '  "installedAt": "%s"\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '}\n'
  } > "$tmp"
  mv "$tmp" "$MANIFEST_FILE"
  echo "  [清单] ${MANIFEST_MODULE} ${MANIFEST_VERSION}（套件 ${SUITE_VERSION}）→ ${MANIFEST_FILE}"
}

# 只更新清单：代码已经手工同步进目标项目，不需要再装一遍
if [ "$MANIFEST_ONLY" -eq 1 ]; then
  write_manifest
  echo ""
  echo "（--manifest-only：只写了清单，没有生成任何文件）"
  exit 0
fi

LAUNCHER="$DEST/overnight-runner"
LAUNCHER_CMD="$DEST/overnight-runner.cmd"
RUNNER_CFG="$DEST/overnight-runner.yaml"
PROJECT_CFG="$DEST/project.yaml"
LEGACY_ROOT_CFG="$PROJECT_ROOT/overnight-runner.yaml"
LEGACY_TOOLS_DIR="$PROJECT_ROOT/$LEGACY_TOOLS"

# ── 找 python ──────────────────────────────────────────────────────
PYTHON=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    if "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
      PYTHON="$c"
      break
    fi
  fi
done
if [ -z "$PYTHON" ]; then
  echo "错误：找不到 Python 3.9+。请先安装 Python。" >&2
  exit 1
fi

echo "overnight-runner 安装器"
echo "  模板目录 : $INSTALLER_DIR"
echo "  目标项目 : $PROJECT_ROOT"
echo "  安装位置 : $TARGET_DIR"
echo "  Python   : $PYTHON ($($PYTHON -V 2>&1))"
echo ""

if [ ! -d "$PKG_DIR" ]; then
  echo "错误：找不到 runner 包 $PKG_DIR" >&2
  exit 1
fi

# ── 拷贝代码（只替换 overnight_runner 包，不删 queue / 配置）────────
if [ -d "$PKG_DEST" ] && [ "$FORCE" -eq 0 ]; then
  echo "  [跳过] $TARGET_DIR/overnight_runner 已存在（用 --force 覆盖）"
  SKIP_CODE=1
else
  SKIP_CODE=0
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 安装 runner 代码 → $PKG_DEST"
  else
    mkdir -p "$DEST"
    rm -rf "$PKG_DEST"
    cp -R "$PKG_DIR" "$PKG_DEST"
    echo "  [安装] runner 代码 → $PKG_DEST"
  fi
fi

# ── 启动脚本 ───────────────────────────────────────────────────────
if [ -f "$LAUNCHER" ] && [ "$FORCE" -eq 0 ] && [ "$SKIP_CODE" -eq 1 ]; then
  echo "  [跳过] 启动脚本已存在（用 --force 覆盖）"
elif [ "$DRY_RUN" -eq 1 ]; then
  echo "  [计划] 生成 $TARGET_DIR/overnight-runner 启动脚本"
else
  mkdir -p "$DEST"
  cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# overnight-runner 启动脚本（由 install.sh 生成）
set -euo pipefail
DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PYTHONPATH="\$DIR\${PYTHONPATH:+:\$PYTHONPATH}" export PYTHONPATH
exec "$PYTHON" -m overnight_runner "\$@"
EOF
  chmod +x "$LAUNCHER"

  cat > "$LAUNCHER_CMD" <<EOF
@echo off
REM overnight-runner 启动脚本（Windows，由 install.sh 生成）
setlocal
set "DIR=%~dp0"
set "PYTHONPATH=%DIR%;%PYTHONPATH%"
"$PYTHON" -m overnight_runner %*
EOF
  echo "  [安装] 启动脚本 → $TARGET_DIR/overnight-runner(.cmd)"
fi

# ── 清理旧 tools/overnight-runner ──────────────────────────────────
if [ -d "$LEGACY_TOOLS_DIR" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 删除旧目录 $LEGACY_TOOLS"
  else
    rm -rf "$LEGACY_TOOLS_DIR"
    # 若 tools/ 已空则删掉
    if [ -d "$PROJECT_ROOT/tools" ] && [ -z "$(ls -A "$PROJECT_ROOT/tools" 2>/dev/null || true)" ]; then
      rmdir "$PROJECT_ROOT/tools" 2>/dev/null || true
    fi
    echo "  [清理] 已删除旧目录 $LEGACY_TOOLS"
  fi
fi

# ── 依赖 ───────────────────────────────────────────────────────────
if [ "$DRY_RUN" -eq 1 ]; then
  echo "  [计划] 校验 Python 可用（已通过：$($PYTHON -V 2>&1)）"
fi

# ── 配置文件 ───────────────────────────────────────────────────────
if [ "$NO_CONFIG" -eq 0 ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 创建 $TARGET_DIR/overnight-runner.yaml 与 project.yaml"
  else
    mkdir -p "$DEST"

    # 根目录旧配置 → .overnight-runner/
    if [ -f "$LEGACY_ROOT_CFG" ] && [ ! -f "$RUNNER_CFG" ]; then
      mv "$LEGACY_ROOT_CFG" "$RUNNER_CFG"
      echo "  [迁移] overnight-runner.yaml → $TARGET_DIR/"
    elif [ -f "$LEGACY_ROOT_CFG" ] && [ -f "$RUNNER_CFG" ]; then
      echo "  [保留] $TARGET_DIR/overnight-runner.yaml 已存在（根目录仍有旧文件，请自行确认后删除）"
    fi

    if [ ! -f "$RUNNER_CFG" ]; then
      cp "$INSTALLER_DIR/config/overnight-runner.example.yaml" "$RUNNER_CFG"
      echo "  [安装] 运行配置 → $TARGET_DIR/overnight-runner.yaml"
    else
      echo "  [保留] $TARGET_DIR/overnight-runner.yaml 已存在"
    fi

    if [ ! -f "$PROJECT_CFG" ]; then
      cp "$INSTALLER_DIR/config/project.example.yaml" "$PROJECT_CFG"
      echo "  [安装] 项目配置 → $TARGET_DIR/project.yaml"
    else
      echo "  [保留] $TARGET_DIR/project.yaml 已存在"
    fi
  fi
else
  echo "  [跳过] 未创建配置文件（--no-config）"
fi

# ── gitignore 提醒 ─────────────────────────────────────────────────
if [ "$NO_CONFIG" -eq 0 ]; then
  NEED_IGNORE=1
  DIR="$PROJECT_ROOT"
  while [ "$DIR" != "/" ] && [ -n "$DIR" ]; do
    if [ -f "$DIR/.gitignore" ] && grep -q "overnight-runner/queue" "$DIR/.gitignore" 2>/dev/null; then
      NEED_IGNORE=0
      break
    fi
    DIR="$(dirname "$DIR")"
  done
  if [ "$NEED_IGNORE" -eq 1 ]; then
    echo ""
    echo "提示：把运行时状态加进 .gitignore（保留 project.yaml / queue.yaml / decisions.jsonl）："
    echo "     **/.overnight-runner/queue/*/state.json"
    echo "     **/.overnight-runner/queue/*/logs/"
    echo "     **/.overnight-runner/queue/*/.lock"
  fi
fi

write_manifest

echo ""
echo "完成。"
echo ""
echo "下一步："
echo "  1) 编辑 $TARGET_DIR/overnight-runner.yaml 配 agent / 看门狗 / 决策模式"
echo "  2) 编辑 $TARGET_DIR/project.yaml 配默认提示词与默认决策规则"
echo "  3) 追加任务：$TARGET_DIR/overnight-runner add docs/plans/xxx.md"
echo "  4) 启动面板：$TARGET_DIR/overnight-runner run"
echo "  5) 多队列：$TARGET_DIR/overnight-runner --queue alice add docs/plans/yyy.md"
