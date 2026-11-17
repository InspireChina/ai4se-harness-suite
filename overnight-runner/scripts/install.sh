#!/usr/bin/env bash
# 把 overnight-runner 安装到目标项目。
#
# 用法：
#   ./install.sh <目标项目目录> [--dry-run] [--force] [--no-config]
#
#   --dry-run     只打印将要发生的改动，不写文件
#   --force       覆盖已存在的 runner 代码
#   --no-config   不创建队列配置与项目配置
#
# 零依赖：只用 Python 3.9+ 标准库，不需要 pip install。

set -euo pipefail

INSTALLER_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PKG_DIR="$INSTALLER_DIR/overnight_runner"
TARGET_TOOLS="tools/overnight-runner"

DRY_RUN=0
FORCE=0
NO_CONFIG=0

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)   DRY_RUN=1 ;;
    --force)     FORCE=1 ;;
    --no-config) NO_CONFIG=1 ;;
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
DEST="$PROJECT_ROOT/$TARGET_TOOLS"

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
echo "  安装位置 : $TARGET_TOOLS"
echo "  Python   : $PYTHON ($($PYTHON -V 2>&1))"
echo ""

if [ ! -d "$PKG_DIR" ]; then
  echo "错误：找不到 runner 包 $PKG_DIR" >&2
  exit 1
fi

# ── 拷贝代码 ───────────────────────────────────────────────────────
if [ -d "$DEST" ] && [ "$FORCE" -eq 0 ]; then
  echo "  [跳过] $TARGET_TOOLS 已存在（用 --force 覆盖）"
else
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 安装 runner 代码 → $DEST"
  else
    rm -rf "$DEST"
    mkdir -p "$DEST"
    cp -R "$PKG_DIR" "$DEST/overnight_runner"
    echo "  [安装] runner 代码 → $DEST"
  fi
fi

# ── 启动脚本 ───────────────────────────────────────────────────────
if [ "$DRY_RUN" -eq 1 ]; then
  echo "  [计划] 生成 overnight-runner 启动脚本"
else
  cat > "$DEST/overnight-runner" <<EOF
#!/usr/bin/env bash
# overnight-runner 启动脚本（由 install.sh 生成）
set -euo pipefail
DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PYTHONPATH="\$DIR\${PYTHONPATH:+:\$PYTHONPATH}" export PYTHONPATH
exec "$PYTHON" -m overnight_runner "\$@"
EOF
  chmod +x "$DEST/overnight-runner"

  cat > "$DEST/overnight-runner.cmd" <<EOF
@echo off
REM overnight-runner 启动脚本（Windows，由 install.sh 生成）
setlocal
set "DIR=%~dp0"
set "PYTHONPATH=%DIR%;%PYTHONPATH%"
"$PYTHON" -m overnight_runner %*
EOF
  echo "  [安装] 启动脚本 → overnight-runner / overnight-runner.cmd"
fi

# ── 依赖 ───────────────────────────────────────────────────────────
# 零依赖：只用 Python 3.9+ 标准库
if [ "$DRY_RUN" -eq 1 ]; then
  echo "  [计划] 校验 Python 可用（已通过：$($PYTHON -V 2>&1)）"
fi

# ── 配置文件 ───────────────────────────────────────────────────────
if [ "$NO_CONFIG" -eq 0 ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 创建 overnight-runner.yaml 与 .overnight-runner/project.yaml"
  else
    if [ ! -f "$PROJECT_ROOT/overnight-runner.yaml" ]; then
      cp "$INSTALLER_DIR/config/overnight-runner.example.yaml" "$PROJECT_ROOT/overnight-runner.yaml"
      echo "  [安装] 运行配置 → overnight-runner.yaml"
    else
      echo "  [保留] overnight-runner.yaml 已存在"
    fi

    mkdir -p "$PROJECT_ROOT/.overnight-runner"
    if [ ! -f "$PROJECT_ROOT/.overnight-runner/project.yaml" ]; then
      cp "$INSTALLER_DIR/config/project.example.yaml" "$PROJECT_ROOT/.overnight-runner/project.yaml"
      echo "  [安装] 项目配置 → .overnight-runner/project.yaml"
    else
      echo "  [保留] .overnight-runner/project.yaml 已存在"
    fi
  fi
else
  echo "  [跳过] 未创建配置文件（--no-config）"
fi

# ── gitignore 提醒 ─────────────────────────────────────────────────
# 逐层往上找 .gitignore（项目自己的 / 仓库根的），找到已排除队列运行时产物的就不提醒
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

echo ""
echo "完成。"
echo ""
echo "下一步："
echo "  1) 编辑 overnight-runner.yaml 配 agent / 看门狗 / 决策模式"
echo "  2) 编辑 .overnight-runner/project.yaml 配默认提示词与默认决策规则"
echo "  3) 追加任务：$TARGET_TOOLS/overnight-runner add docs/plans/xxx.md"
echo "  4) 启动面板：$TARGET_TOOLS/overnight-runner run"
echo "  5) 多队列：$TARGET_TOOLS/overnight-runner --queue alice add docs/plans/yyy.md"
