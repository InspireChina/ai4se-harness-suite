#!/usr/bin/env bash
# 安装 Agile Team SDD 技能套件到指定项目。
#
# 用法：
#   ./install.sh <目标项目目录> [--group <g>] [--skill <name>] [--list] [--dry-run] [--force] [--no-config]
#
#   --group <g>     只安装某一组（ba / dev / qa / pm / tl），可重复
#   --skill <name>  只安装指定 skill，可重复
#   --list          列出全部可用 skill 并退出
#   --dry-run       只打印将要发生的改动，不写文件
#   --force         覆盖目标项目里已存在的同名 skill
#   --no-config     不修改目标项目的 opencode.jsonc

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_SKILLS_DIR="$SKILL_DIR/skills"
CATALOG_FILE="$SKILL_DIR/catalog.json"

DRY_RUN=0
FORCE=0
NO_CONFIG=0
LIST_ONLY=0
SEL_GROUPS=()
SEL_SKILLS=()

usage() {
  sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)   DRY_RUN=1 ;;
    --force)     FORCE=1 ;;
    --no-config) NO_CONFIG=1 ;;
    --list)      LIST_ONLY=1 ;;
    --group)     SEL_GROUPS+=("$(echo "${2:-}" | tr -d '[:space:]')"); shift ;;
    --skill)     SEL_SKILLS+=("$(echo "${2:-}" | tr -d '[:space:]')"); shift ;;
    -h|--help)   usage 0 ;;
    -*)          echo "未知参数: $1" >&2; usage 1 ;;
    *)           TARGET="$1" ;;
  esac
  shift
done

if [ "$LIST_ONLY" -eq 1 ]; then
  if command -v node >/dev/null 2>&1 && [ -f "$CATALOG_FILE" ]; then
    node -e '
      const c = require(process.argv[1]);
      for (const [g, items] of Object.entries(c)) {
        console.log("\n" + g);
        for (const s of items) console.log("  " + s.name.padEnd(24) + s.description);
      }
      console.log("");
    ' "$CATALOG_FILE"
  else
    for d in "$SOURCE_SKILLS_DIR"/*/; do
      [ -d "$d" ] || continue
      printf "  %s\n" "$(basename "$d")"
    done
  fi
  exit 0
fi

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

# ── 目录与文件 ───────────────────────────────────────────────────────
SKILLS_DIR="${SKILLS_DIR:-.agents/skills}"
BACKEND_DIR="${BACKEND_DIR:-containers/backend}"
FRONTEND_DIR="${FRONTEND_DIR:-containers/frontend}"
E2E_DIR="${E2E_DIR:-e2e}"
DOCS_DIR="${DOCS_DIR:-docs}"
AGENTS_FILE="${AGENTS_FILE:-AGENTS.md}"
MCP_CONFIG_FILE="${MCP_CONFIG_FILE:-.mcp.json}"
E2E_RUNNER="${E2E_RUNNER:-e2e-run.sh}"
if [ "$PATH_MODE" = "relative" ]; then
  case "$E2E_RUNNER" in
    /*|./*) ;;
    *) E2E_RUNNER="./$E2E_RUNNER" ;;
  esac
fi

FEATURES_DIR="${FEATURES_DIR:-$DOCS_DIR/features}"
CHORES_DIR="${CHORES_DIR:-$FEATURES_DIR/_chores}"
PLANS_DIR="${PLANS_DIR:-$CHORES_DIR}"
FACTS_DIR="${FACTS_DIR:-$DOCS_DIR/facts}"
BUSINESS_FACTS_DIR="${BUSINESS_FACTS_DIR:-$FACTS_DIR/business}"
TECH_TOPIC_DIR="${TECH_TOPIC_DIR:-$FACTS_DIR/tech-topic}"
STANDARDS_DIR="${STANDARDS_DIR:-$DOCS_DIR/standards}"
TEST_CASES_DIR="${TEST_CASES_DIR:-$DOCS_DIR/test-cases}"
E2E_CASES_DIR="${E2E_CASES_DIR:-$TEST_CASES_DIR/e2e-cases}"
MANUAL_CASES_DIR="${MANUAL_CASES_DIR:-$TEST_CASES_DIR/manual-cases}"
SMOKING_CASES_DIR="${SMOKING_CASES_DIR:-$TEST_CASES_DIR/smoking-cases}"
DEV_SELF_CASES_DIR="${DEV_SELF_CASES_DIR:-$TEST_CASES_DIR/dev-self-cases}"
RELEASES_DIR="${RELEASES_DIR:-$DOCS_DIR/releases}"

TARGET_BRANCH="${TARGET_BRANCH:-main}"
BACKEND_PORT="${BACKEND_PORT:-8080}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

# harness 套件自身所在目录（pm-retro 需要回写模板时用）
HARNESS_ROOT="${HARNESS_ROOT:-$(cd "$SKILL_DIR/.." && pwd)}"

TEST_CMD_BACKEND="${TEST_CMD_BACKEND:-cd $BACKEND_DIR && mvn test}"
TEST_CMD_FRONTEND="${TEST_CMD_FRONTEND:-cd $FRONTEND_DIR && npm run build}"

# ── 路径模式 ───────────────────────────────────────────────────────
# absolute（默认）：渲染成绝对路径，skill 在任意 cwd 下都可用
# relative        ：渲染成项目相对路径，仓库可移植（会随仓库分发时用）
PATH_MODE="${PATH_MODE:-absolute}"

# 把项目内路径拼成最终值
proj_path() {
  if [ "$PATH_MODE" = "relative" ]; then
    printf '%s' "$1"
  else
    printf '%s/%s' "$PROJECT_ROOT" "$1"
  fi
}

# 计算某个绝对路径相对于项目根的路径（相对模式用；跨仓库时也保持可移植）
rel_to_project() {
  local target="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' "$target" "$PROJECT_ROOT" 2>/dev/null && return 0
  fi
  printf '%s' "$target"
}

# ── 占位符表（从长到短，后面的可引用前面的）────────────────────────
PAIRS=(
  "TEST_CMD_BACKEND=$TEST_CMD_BACKEND"
  "TEST_CMD_FRONTEND=$TEST_CMD_FRONTEND"
  "SPEC_TEMPLATE=$(proj_path "$FEATURES_DIR/_template/spec.md")"
  "PLAN_TEMPLATE=$(proj_path "$FEATURES_DIR/_template/plan.md")"
  "DOMAIN_MODEL_DOC=$(proj_path "$FACTS_DIR/domain-model.md")"
  "API_SPEC=$(proj_path "$FACTS_DIR/api.yaml")"
  "DB_SCHEMA_DOC=$(proj_path "$FACTS_DIR/db-schema.md")"
  "BUSINESS_RULES_DOC=$(proj_path "$TECH_TOPIC_DIR/businessrule.md")"
  "DATA_DICT_DOC=$(proj_path "$TECH_TOPIC_DIR/data-dict.md")"
  "MANUAL_CASES_DIR=$(proj_path "$MANUAL_CASES_DIR")"
  "SMOKING_CASES_DIR=$(proj_path "$SMOKING_CASES_DIR")"
  "DEV_SELF_CASES_DIR=$(proj_path "$DEV_SELF_CASES_DIR")"
  "RELEASES_DIR=$(proj_path "$RELEASES_DIR")"
  "E2E_CASES_DIR=$(proj_path "$E2E_CASES_DIR")"
  "TEST_CASES_DIR=$(proj_path "$TEST_CASES_DIR")"
  "STANDARDS_DIR=$(proj_path "$STANDARDS_DIR")"
  "CHORES_DIR=$(proj_path "$CHORES_DIR")"
  "FEATURES_DIR=$(proj_path "$FEATURES_DIR")"
  "PLANS_DIR=$(proj_path "$PLANS_DIR")"
  "BUSINESS_FACTS_DIR=$(proj_path "$BUSINESS_FACTS_DIR")"
  "TECH_TOPIC_DIR=$(proj_path "$TECH_TOPIC_DIR")"
  "FACTS_DIR=$(proj_path "$FACTS_DIR")"
  "DOCS_DIR=$(proj_path "$DOCS_DIR")"
  "E2E_RUNNER=$(proj_path "$E2E_RUNNER")"
  "E2E_DIR=$(proj_path "$E2E_DIR")"
  "FRONTEND_DIR=$(proj_path "$FRONTEND_DIR")"
  "BACKEND_DIR=$(proj_path "$BACKEND_DIR")"
  "MCP_CONFIG_FILE=$(proj_path "$MCP_CONFIG_FILE")"
  "SKILLS_DIR=$(proj_path "$SKILLS_DIR")"
  "AGENTS_FILE=$(proj_path "$AGENTS_FILE")"
  "TARGET_BRANCH=$TARGET_BRANCH"
  "BACKEND_PORT=$BACKEND_PORT"
  "FRONTEND_PORT=$FRONTEND_PORT"
  "HARNESS_ROOT=$( [ "$PATH_MODE" = "relative" ] && rel_to_project "$HARNESS_ROOT" || printf '%s' "$HARNESS_ROOT" )"
  "PROJECT_NAME=$PROJECT_NAME"
  "PROJECT_ROOT=$( [ "$PATH_MODE" = "relative" ] && printf '.' || printf '%s' "$PROJECT_ROOT" )"
)

escape_replacement() {
  printf '%s' "$1" | sed -e 's/[\\&|]/\\&/g'
}

render() {
  local file="$1" out="$2" template_name="$3" skill_name="$4"
  local args=()
  local pair key value
  for pair in "${PAIRS[@]}"; do
    key="${pair%%=*}"
    value="${pair#*=}"
    args+=(-e "s|{{$key}}|$(escape_replacement "$value")|g")
  done
  sed "${args[@]}" "$file" \
    | awk '
        /<!-- TEMPLATE-ONLY -->/          { skip=1; next }
        skip==1 && /<!-- \/TEMPLATE-ONLY -->/ { skip=0; dropblank=1; next }
        skip==1                           { next }
        dropblank==1 && /^[[:space:]]*$/  { dropblank=0; next }
                                       { dropblank=0; print }
      ' \
    | sed -e "s/^name: ${template_name}\$/name: ${skill_name}/" \
    > "$out"
}

# ── 选择要安装的 skill ───────────────────────────────────────────────
# 过滤逻辑：--group / --skill 命中即选中；两者都不给则全装。
select_templates() {
  local d template_name name
  for d in "$SOURCE_SKILLS_DIR"/*/; do
    [ -d "$d" ] || continue
    template_name="$(basename "$d")"
    name="${template_name%-template}"

    if [ ${#SEL_GROUPS[@]} -eq 0 ] && [ ${#SEL_SKILLS[@]} -eq 0 ]; then
      echo "$d"
      continue
    fi

    local matched=0
    for g in ${SEL_GROUPS[@]+"${SEL_GROUPS[@]}"}; do
      [ -n "$g" ] || continue
      if catalog_has_group "$g" "$name"; then matched=1; break; fi
    done
    for s in ${SEL_SKILLS[@]+"${SEL_SKILLS[@]}"}; do
      [ -n "$s" ] || continue
      if [ "$s" = "$name" ] || [ "$s" = "$template_name" ]; then matched=1; break; fi
    done
    [ "$matched" -eq 1 ] && echo "$d"
  done
}

# 从 catalog.json 查某个 skill 属于哪些组
catalog_has_group() {
  local group="$1" skill="$2"
  [ -f "$CATALOG_FILE" ] || return 1
  command -v node >/dev/null 2>&1 || return 1
  node -e '
    const c = require(process.argv[1]);
    const [g, s] = [process.argv[2], process.argv[3]];
    process.exit((c[g] || []).some(x => x.name === s) ? 0 : 1);
  ' "$CATALOG_FILE" "$group" "$skill"
}

# ── 安装 ─────────────────────────────────────────────────────────────
TARGET_SKILLS_DIR="$PROJECT_ROOT/$SKILLS_DIR"

echo "Agile Team SDD 安装器"
echo "  模板目录 : $SOURCE_SKILLS_DIR"
echo "  目标项目 : $PROJECT_ROOT"
echo "  skills 目录: $TARGET_SKILLS_DIR"
echo "  路径模式  : $PATH_MODE"
if [ ${#SEL_GROUPS[@]} -gt 0 ]; then echo "  分组过滤 : ${SEL_GROUPS[*]}"; fi
if [ ${#SEL_SKILLS[@]} -gt 0 ]; then echo "  指定 skill: ${SEL_SKILLS[*]}"; fi
echo ""

if [ ! -d "$SOURCE_SKILLS_DIR" ]; then
  echo "错误：找不到模板目录 $SOURCE_SKILLS_DIR" >&2
  exit 1
fi

installed=0
skipped=0
TEMPLATES=()
while IFS= read -r d; do
  [ -n "$d" ] && TEMPLATES+=("$d")
done < <(select_templates)

if [ ${#TEMPLATES[@]} -eq 0 ]; then
  echo "错误：没有匹配的 skill。用 --list 查看全部。" >&2
  exit 1
fi

for d in "${TEMPLATES[@]}"; do
  template_name="$(basename "$d")"
  # 模板目录名去掉 -template 后缀，即安装后的 skill 名
  name="${template_name%-template}"
  dest_dir="$TARGET_SKILLS_DIR/$name"

  if [ -f "$dest_dir/SKILL.md" ] && [ "$FORCE" -eq 0 ]; then
    echo "  [跳过] ${name}（已存在，用 --force 覆盖）"
    skipped=$((skipped + 1))
    continue
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 安装 ${name} → $dest_dir/"
  else
    rm -rf "$dest_dir"
    mkdir -p "$dest_dir"
    # 整个模板目录一起复制，附属文件（baseline.md 等）也渲染
    while IFS= read -r f; do
      rel="${f#$d}"
      mkdir -p "$(dirname "$dest_dir/$rel")"
      render "$f" "$dest_dir/$rel" "$template_name" "$name"
    done < <(find "$d" -type f | sort)
    echo "  [安装] ${name} → $dest_dir/"
  fi
  installed=$((installed + 1))
done

# ── 注册 skills 路径 ─────────────────────────────────────────────────
CONFIG_FILE="$PROJECT_ROOT/opencode.jsonc"
if [ "$NO_CONFIG" -eq 0 ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [计划] 在 $CONFIG_FILE 中注册 skills.paths = [\"$SKILLS_DIR\"]"
  elif [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",

  "skills": {
    "paths": ["$SKILLS_DIR"]
  }
}
EOF
    echo "  [创建] $CONFIG_FILE"
  elif grep -q '"skills"' "$CONFIG_FILE"; then
    echo "  [保留] $CONFIG_FILE 已包含 skills 配置，请人工确认路径是否为 \"$SKILLS_DIR\""
  else
    # 在最外层对象的第一个 "{" 之后插入 skills 段
    perl -0pi -e "s/(\{\s*\n)/\$1  \"skills\": {\n    \"paths\": [\"$SKILLS_DIR\"]\n  },\n/" "$CONFIG_FILE"
    echo "  [更新] $CONFIG_FILE 已注册 skills.paths"
  fi
fi

# ── 残留占位符检查 ───────────────────────────────────────────────────
if [ "$DRY_RUN" -eq 0 ]; then
  leftovers="$(grep -rhoE '\{\{[A-Z_]+\}\}' "$TARGET_SKILLS_DIR" 2>/dev/null | sort -u || true)"
  if [ -n "$leftovers" ]; then
    echo ""
    echo "警告：以下占位符未被替换，请检查："
    echo "$leftovers" | sed 's/^/  - /'
  fi
fi

echo ""
echo "完成：安装 $installed 个 skill，跳过 $skipped 个。"
echo "提示：修改 opencode 配置后需重启 opencode 才会生效。"
