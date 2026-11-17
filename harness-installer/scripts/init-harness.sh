#!/usr/bin/env bash
# 初始化项目的 harness：AGENTS.md + docs/ 文档骨架 + opencode 配置。
#
# 用法：
#   ./init-harness.sh <目标项目目录> [--dry-run] [--force] [--no-agents]
#
#   --dry-run     只打印将要发生的改动，不写文件
#   --force       覆盖目标项目里已存在的 AGENTS.md / 文档文件
#   --no-agents   不生成 AGENTS.md，只生成 docs/ 骨架

set -euo pipefail

INSTALLER_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$INSTALLER_DIR/templates"

DRY_RUN=0
FORCE=0
NO_AGENTS=0

usage() {
  sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)   DRY_RUN=1 ;;
    --force)     FORCE=1 ;;
    --no-agents) NO_AGENTS=1 ;;
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
PROJECT_NAME="${PROJECT_NAME:-$(basename "$PROJECT_ROOT")}"

# ── 自动探测项目结构 ────────────────────────────────────────────────
detect_dir() {
  # detect_dir <候选1> <候选2> ... <探测文件>
  local candidate found=""
  local probe="${!#}"
  for candidate in "${@:1:$#-1}"; do
    if [ -e "$PROJECT_ROOT/$candidate/$probe" ]; then
      found="$candidate"
      break
    fi
  done
  echo "$found"
}

BACKEND_DIR="${BACKEND_DIR:-$(detect_dir backend service server api pom.xml)}"
[ -z "$BACKEND_DIR" ] && BACKEND_DIR="backend"
FRONTEND_DIR="${FRONTEND_DIR:-$(detect_dir frontend web client ui package.json)}"
[ -z "$FRONTEND_DIR" ] && FRONTEND_DIR="frontend"
E2E_DIR="${E2E_DIR:-$(detect_dir e2e tests test package.json)}"
[ -z "$E2E_DIR" ] && E2E_DIR="e2e"
DOCS_DIR="${DOCS_DIR:-docs}"
E2E_CASES_DIR="${E2E_CASES_DIR:-$DOCS_DIR/test-cases/e2e-cases}"
E2E_RUNNER="${E2E_RUNNER:-e2e-run.sh}"
FEATURES_DIR="${FEATURES_DIR:-$DOCS_DIR/features}"
PLANS_DIR="${PLANS_DIR:-$DOCS_DIR/plans}"
DESIGNS_DIR="${DESIGNS_DIR:-$DOCS_DIR/designs}"
STANDARDS_DIR="${STANDARDS_DIR:-$DOCS_DIR/standards}"

BACKEND_DESC="${BACKEND_DESC:-后端服务}"
FRONTEND_DESC="${FRONTEND_DESC:-前端应用}"
BACKEND_NAME="${BACKEND_NAME:-后端服务}"
FRONTEND_NAME="${FRONTEND_NAME:-前端应用}"
DATABASE="${DATABASE:-数据库}"
TECH_STACK="${TECH_STACK:-见项目 README}"
ERROR_CODE_EXAMPLE="${ERROR_CODE_EXAMPLE:-BUSINESS_ERROR}"
ERROR_MESSAGE_EXAMPLE="${ERROR_MESSAGE_EXAMPLE:-业务规则不满足}"

# ── 占位符表（从长到短）──────────────────────────────────────────────
PAIRS=(
  "TECH_STACK=$TECH_STACK"
  "BACKEND_DESC=$BACKEND_DESC"
  "FRONTEND_DESC=$FRONTEND_DESC"
  "BACKEND_NAME=$BACKEND_NAME"
  "FRONTEND_NAME=$FRONTEND_NAME"
  "DATABASE=$DATABASE"
  "ERROR_CODE_EXAMPLE=$ERROR_CODE_EXAMPLE"
  "ERROR_MESSAGE_EXAMPLE=$ERROR_MESSAGE_EXAMPLE"
  "TEST_CMD_BACKEND=cd $PROJECT_ROOT/$BACKEND_DIR && mvn test"
  "TEST_CMD_FRONTEND=cd $PROJECT_ROOT/$FRONTEND_DIR && npm run build"
  "E2E_CASES_DIR=$PROJECT_ROOT/$E2E_CASES_DIR"
  "E2E_RUNNER=$PROJECT_ROOT/$E2E_RUNNER"
  "E2E_DIR=$PROJECT_ROOT/$E2E_DIR"
  "STANDARDS_DIR=$PROJECT_ROOT/$STANDARDS_DIR"
  "DESIGNS_DIR=$PROJECT_ROOT/$DESIGNS_DIR"
  "PLANS_DIR=$PROJECT_ROOT/$PLANS_DIR"
  "FEATURES_DIR=$PROJECT_ROOT/$FEATURES_DIR"
  "DOCS_DIR=$PROJECT_ROOT/$DOCS_DIR"
  "FRONTEND_DIR=$PROJECT_ROOT/$FRONTEND_DIR"
  "BACKEND_DIR=$PROJECT_ROOT/$BACKEND_DIR"
  "PROJECT_NAME=$PROJECT_NAME"
  "PROJECT_ROOT=$PROJECT_ROOT"
)

escape_replacement() {
  printf '%s' "$1" | sed -e 's/[\\&|]/\\&/g'
}

render() {
  local file="$1" out="$2"
  local args=()
  local pair key value
  for pair in "${PAIRS[@]}"; do
    key="${pair%%=*}"
    value="${pair#*=}"
    args+=(-e "s|{{$key}}|$(escape_replacement "$value")|g")
  done
  sed "${args[@]}" "$file" > "$out"
}

# ── 执行 ─────────────────────────────────────────────────────────────
created=0
skipped=0

write_file() {
  local src="$1" dest="$2"
  if [ -f "$dest" ] && [ "$FORCE" -eq 0 ]; then
    echo "  [跳过] ${dest#$PROJECT_ROOT/}（已存在，用 --force 覆盖）"
    skipped=$((skipped + 1))
    return
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 生成 ${dest#$PROJECT_ROOT/}"
  else
    mkdir -p "$(dirname "$dest")"
    render "$src" "$dest"
    echo "  [生成] ${dest#$PROJECT_ROOT/}"
  fi
  created=$((created + 1))
}

echo "Harness 初始化器"
echo "  模板目录 : $TEMPLATE_DIR"
echo "  目标项目 : $PROJECT_ROOT"
echo "  探测结果 : backend=$BACKEND_DIR frontend=$FRONTEND_DIR e2e=$E2E_DIR docs=$DOCS_DIR"
echo ""

if [ "$NO_AGENTS" -eq 0 ]; then
  write_file "$TEMPLATE_DIR/AGENTS.md.template" "$PROJECT_ROOT/AGENTS.md"
fi

# docs/ 骨架：递归拷贝模板目录
while IFS= read -r src; do
  rel="${src#$TEMPLATE_DIR/docs/}"
  write_file "$src" "$PROJECT_ROOT/$DOCS_DIR/$rel"
done <<EOF
$(find "$TEMPLATE_DIR/docs" -type f | sort)
EOF

# opencode 配置
CONFIG_FILE="$PROJECT_ROOT/opencode.jsonc"
if [ ! -f "$CONFIG_FILE" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 生成 opencode.jsonc"
  else
    cp "$TEMPLATE_DIR/opencode.jsonc" "$CONFIG_FILE"
    echo "  [生成] opencode.jsonc"
  fi
  created=$((created + 1))
else
  echo "  [保留] opencode.jsonc（已存在）"
  skipped=$((skipped + 1))
fi

echo ""
echo "完成：生成 $created 个文件，跳过 $skipped 个。"
echo "下一步："
echo "  1. 填写 AGENTS.md 中所有 TODO 段落（技术栈、分层、鉴权、测试规范等）"
echo "  2. 执行 agile-team-sdd/install.sh $PROJECT_ROOT 安装 SDD skills"
echo "  3. 执行 tool-chain-installer 安装 MCP 工具链"
echo "提示：修改 opencode 配置后需重启 opencode 才会生效。"
