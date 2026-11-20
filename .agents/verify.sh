#!/usr/bin/env bash
# 一键验证本仓库。
#
# 用法：
#   ./.agents/verify.sh              # 全部检查
#   ./.agents/verify.sh --fast       # 跳过 overnight-runner 冒烟测试
#
# 退出码：0 全绿，1 有失败。

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FAST=0
[ "${1:-}" = "--fast" ] && FAST=1

FAILED=0
PASSED=0

ok()   { PASSED=$((PASSED + 1)); printf '  \033[32m✔\033[0m %s\n' "$1"; }
bad()  { FAILED=$((FAILED + 1)); printf '  \033[31m✘\033[0m %s\n' "$1"; }
skip() { printf '  \033[90m—\033[0m %s\n' "$1"; }
head_() { printf '\n\033[1m%s\033[0m\n' "$1"; }

# ── 1. Bash 语法 ───────────────────────────────────────────────────
head_ "1. Bash 语法"
while IFS= read -r f; do
  if bash -n "$f" 2>/dev/null; then ok "$f"; else bad "$f"; bash -n "$f"; fi
done < <(find . -name "*.sh" -not -path "./.git/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" | sort)

# ── 2. Python 语法 ─────────────────────────────────────────────────
head_ "2. Python 语法"
PY=""
for c in python3 python; do
  command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
done
if [ -z "$PY" ]; then
  skip "找不到 python"
else
  while IFS= read -r f; do
    if "$PY" -m py_compile "$f" 2>/dev/null; then ok "$f"; else bad "$f"; "$PY" -m py_compile "$f"; fi
  done < <(find . -name "*.py" -not -path "./.git/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" | sort)
  find . -name "__pycache__" -type d -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null
fi

# ── 3. Node 语法 ───────────────────────────────────────────────────
head_ "3. Node 语法"
if ! command -v node >/dev/null 2>&1; then
  skip "找不到 node"
else
  while IFS= read -r f; do
    if node --check "$f" 2>/dev/null; then ok "$f"; else bad "$f"; node --check "$f"; fi
  done < <(find . -name "*.mjs" -o -name "*.js" -not -path "./.git/*" -not -path "*/node_modules/*" | grep -v node_modules | sort)
fi

# ── 4. JSON / YAML 可解析 ──────────────────────────────────────────
head_ "4. JSON / YAML 可解析"
if [ -n "$PY" ]; then
  "$PY" - <<'PYEOF'
import json, pathlib, sys
import yaml

bad = []
files = [
    p for p in pathlib.Path('.').rglob('*')
    if p.suffix in ('.json', '.jsonc', '.yaml', '.yml')
    and '.git/' not in str(p) and '.venv/' not in str(p)
    and 'node_modules' not in str(p)
]
for p in sorted(files):
    try:
        if p.suffix in ('.json', '.jsonc'):
            json.loads(p.read_text(encoding='utf-8'))
        else:
            yaml.safe_load(p.read_text(encoding='utf-8'))
        print(f'  \033[32m✔\033[0m {p}')
    except Exception as exc:
        print(f'  \033[31m✘\033[0m {p} — {exc}')
        bad.append(p)
sys.exit(1 if bad else 0)
PYEOF
  if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
else
  skip "找不到 python"
fi

# ── 5. skill 名/目录一致、无重名 ───────────────────────────────────
head_ "5. skill 名/目录一致、无重名"
if [ -n "$PY" ]; then
  "$PY" - <<'PYEOF'
import collections, pathlib, re, sys

seen = collections.Counter()
bad = []
for md in sorted(pathlib.Path('.').rglob('SKILL.md')):
    s = str(md)
    if '.git/' in s or '.venv/' in s or 'node_modules' in s:
        continue
    m = re.search(r'^name:\s*(\S+)', md.read_text(encoding='utf-8'), re.M)
    if not m:
        print(f'  \033[31m✘\033[0m {md} — 缺少 name')
        bad.append(md)
        continue
    name = m.group(1)
    seen[name] += 1
    if name != md.parent.name:
        print(f'  \033[31m✘\033[0m {md} — name={name} 与目录名 {md.parent.name} 不一致')
        bad.append(md)
for name, n in seen.items():
    if n > 1:
        print(f'  \033[31m✘\033[0m 重名 skill: {name}（{n} 处）')
        bad.append(name)
if not bad:
    print(f'  \033[32m✔\033[0m {sum(seen.values())} 个 skill，名称与目录一致且无重名')
sys.exit(1 if bad else 0)
PYEOF
  if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
else
  skip "找不到 python"
fi

# ── 6. 清单 ↔ 模板 ↔ 已安装 三方一致 ──────────────────────────────
head_ "6. 清单 ↔ 模板 ↔ 已安装 一致"
if [ -n "$PY" ]; then
  "$PY" - <<'PYEOF'
import json, pathlib, re, sys

bad = []
catalog_path = pathlib.Path('agile-team-sdd/catalog.json')
if not catalog_path.exists():
    print('  \033[31m✘\033[0m 缺 agile-team-sdd/catalog.json')
    sys.exit(1)

catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
listed = {s['name'] for g in catalog.values() for s in g}

tpl_root = pathlib.Path('agile-team-sdd/skills')
templates = {p.name.replace('-template', '') for p in tpl_root.iterdir() if p.is_dir()}

installed_root = pathlib.Path('example-project/.agents/skills')
installed = {p.name for p in installed_root.iterdir() if p.is_dir()} if installed_root.exists() else set()

if listed != templates:
    print(f'  \033[31m✘\033[0m 清单与模板不一致：{sorted(listed ^ templates)}')
    bad.append('catalog/templates')
if listed != installed:
    print(f'  \033[31m✘\033[0m 清单与已安装不一致：{sorted(listed ^ installed)}')
    bad.append('catalog/installed')

# 名字对上还不够：模板改了没重装，装进去的就是旧正文。
# 逐行比对，占位符渲染成路径 / 端口 / 分支名，所以按通配比对；TEMPLATE-ONLY 块安装时已删掉。
TPL_ONLY = re.compile(r'<!-- TEMPLATE-ONLY -->.*?<!-- /TEMPLATE-ONLY -->\n\n?', re.S)
PH_SPLIT = re.compile(r'(\{\{[A-Z0-9_]+\}\})')

def line_matches(tpl_line, got_line):
    parts = PH_SPLIT.split(tpl_line)[::2]
    return re.fullmatch('.+?'.join(re.escape(p) for p in parts), got_line) is not None

stale = 0
for d in sorted(tpl_root.iterdir()):
    if not d.is_dir():
        continue
    tpl_name = d.name
    skill = tpl_name[:-len('-template')] if tpl_name.endswith('-template') else tpl_name
    for f in sorted(p for p in d.rglob('*') if p.is_file()):
        target = installed_root / skill / f.relative_to(d)
        if not target.exists():
            print(f'  \033[31m✘\033[0m 项目里缺 {target}（模板有）')
            stale += 1
            continue
        text = TPL_ONLY.sub('', f.read_text(encoding='utf-8')).replace(f'name: {tpl_name}\n', f'name: {skill}\n')
        exp = text.splitlines()
        got = target.read_text(encoding='utf-8').splitlines()
        idx = next((i for i in range(min(len(exp), len(got))) if not line_matches(exp[i], got[i])), None)
        if idx is not None or len(exp) != len(got):
            where = f'第 {idx + 1} 行' if idx is not None else f'行数 {len(exp)} vs {len(got)}'
            print(f'  \033[31m✘\033[0m {target} 落后于模板（{where}）—— 重跑 install.sh --force')
            stale += 1
if stale:
    bad.append('stale-installed')
elif not bad:
    print(f'  \033[32m✔\033[0m 三方一致（{len(listed)} 个 skill），已安装正文与模板一致')
sys.exit(1 if bad else 0)
PYEOF
  if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
else
  skip "找不到 python"
fi

# ── 7. 占位符已登记 + harness-installer 模板可渲染 ────────────────
head_ "7. 模板占位符已登记"
if [ -n "$PY" ]; then
  "$PY" - <<'PYEOF'
import pathlib, re, sys

used = set()
for f in pathlib.Path('agile-team-sdd/skills').rglob('*.md'):
    used |= set(re.findall(r'\{\{([A-Z0-9_]+)\}\}', f.read_text(encoding='utf-8')))

doc = pathlib.Path('agile-team-sdd/placeholders.md')
declared = set(re.findall(r'\{\{([A-Z0-9_]+)\}\}', doc.read_text(encoding='utf-8'))) if doc.exists() else set()

missing = sorted(used - declared)
if missing:
    print(f'  \033[31m✘\033[0m 未登记的占位符：{missing}')
    sys.exit(1)

# harness-installer：模板里用到的占位符必须能被 init-harness.sh 替换
# （它的源码 PAIRS 才是这部分的事实源；placeholders.md 管的是 agile-team-sdd）
tpl = pathlib.Path('harness-installer/templates')
harness_used = set()
for f in tpl.rglob('*'):
    if not f.is_file():
        continue
    try:
        harness_used |= set(re.findall(r'\{\{([A-Z0-9_]+)\}\}', f.read_text(encoding='utf-8')))
    except UnicodeDecodeError:
        continue

script = pathlib.Path('harness-installer/scripts/init-harness.sh').read_text(encoding='utf-8')
substituted = set(re.findall(r'^\s*"([A-Z0-9_]+)=', script, re.M))

problems = []
for ph in sorted(harness_used - substituted):
    problems.append(f'harness-installer 模板里的 {{{{{ph}}}}} 不会被 init-harness.sh 替换')
if problems:
    for p in problems:
        print(f'  \033[31m✘\033[0m {p}')
    sys.exit(1)

print(f'  \033[32m✔\033[0m {len(used)} + {len(harness_used)} 个占位符已登记且可渲染')
PYEOF
  if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
else
  skip "找不到 python"
fi

# ── 8. 已安装 skill 无残留占位符、无绝对路径 ───────────────────────
head_ "8. 已安装 skill 无残留占位符 / 无绝对路径"
if [ -n "$PY" ]; then
  "$PY" - <<'PYEOF'
import pathlib, re, sys

root = pathlib.Path('example-project/.agents/skills')
bad = []
files = sorted(root.rglob('*.md')) if root.exists() else []
for f in files:
    text = f.read_text(encoding='utf-8')
    for ph in re.findall(r'\{\{[A-Z0-9_]+\}\}', text):
        print(f'  \033[31m✘\033[0m {f} — 残留占位符 {ph}')
        bad.append(f)
    for m in re.findall(r'/(?:Users|home)/[^\s`"\')]+', text):
        print(f'  \033[31m✘\033[0m {f} — 泄漏绝对路径 {m}')
        bad.append(f)
if not bad:
    print(f'  \033[32m✔\033[0m {len(files)} 个已安装文件干净')
sys.exit(1 if bad else 0)
PYEOF
  if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
else
  skip "找不到 python"
fi

# ── 9. Markdown 相对链接有效 ───────────────────────────────────────
head_ "9. Markdown 相对链接有效"
if [ -n "$PY" ]; then
  "$PY" - <<'PYEOF'
import pathlib, re, sys

bad = []
checked = 0
for md in pathlib.Path('.').rglob('*.md'):
    s = str(md)
    if '.git/' in s or '.venv/' in s or 'node_modules' in s:
        continue
    text = md.read_text(encoding='utf-8')
    for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)', text):
        link = m.group(1).split('#')[0].strip()
        if not link or link.startswith(('http://', 'https://', 'mailto:')):
            continue
        checked += 1
        if not (md.parent / link).resolve().exists():
            print(f'  \033[31m✘\033[0m {md} → {link}')
            bad.append(link)
if not bad:
    print(f'  \033[32m✔\033[0m {checked} 条相对链接全部有效')
sys.exit(1 if bad else 0)
PYEOF
  if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
else
  skip "找不到 python"
fi

# ── 9.1 harness-installer 骨架 ↔ AGENTS.md 声明一致 ──────────────
head_ "9.1 harness-installer 骨架与声明一致"
if [ -z "$PY" ]; then
  skip "找不到 python"
else
  TMPI="$(mktemp -d)"
  mkdir -p "$TMPI/abs" "$TMPI/rel"
  if ./harness-installer/scripts/init-harness.sh "$TMPI/abs" >/dev/null 2>&1 \
     && PATH_MODE=relative ./harness-installer/scripts/init-harness.sh "$TMPI/rel" >/dev/null 2>&1; then
    "$PY" - "$TMPI" <<'PYEOF'
import pathlib, re, sys

tmp = pathlib.Path(sys.argv[1])
bad = []

abs_text = (tmp / 'abs' / 'AGENTS.md').read_text(encoding='utf-8')
if str(tmp / 'abs') not in abs_text:
    bad.append('absolute 模式未写入绝对路径')

rel_root = tmp / 'rel'
rel_text = (rel_root / 'AGENTS.md').read_text(encoding='utf-8')
if str(tmp) in rel_text:
    bad.append('relative 模式泄漏安装机绝对路径')
for ph in sorted(set(re.findall(r'\{\{[A-Z_]+\}\}', rel_text))):
    bad.append(f'AGENTS.md 残留占位符 {ph}')

# 声明 ↔ 实物：引用的 docs 路径必须存在
#   - docs/facts/ 是 as-built 产物，装机时本就不存在
#   - 含 <...> 的目录每个迭代才创建
for s in sorted(set(re.findall(r'(?<![\w/])docs/[^\s`)、，；,]+', rel_text))):
    s = s.rstrip('/').rstrip('。')
    if s.startswith('docs/facts/') or '<' in s:
        continue
    if not (rel_root / s).exists():
        bad.append(f'AGENTS.md 声明了不存在的路径 {s}')

if bad:
    for b in bad:
        print(f'  \033[31m✘\033[0m {b}')
    sys.exit(1)
print(f'  \033[32m✔\033[0m 骨架与 AGENTS.md 声明一致（abs / rel 双模式）')
PYEOF
    if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
  else
    bad "init-harness.sh 在临时目录安装失败"
  fi
  rm -rf "$TMPI"
fi

# ── 10. overnight-runner 冒烟测试 ─────────────────────────────────
head_ "10. overnight-runner 测试"
if [ "$FAST" -eq 1 ]; then
  skip "--fast 跳过"
elif [ -z "$PY" ]; then
  skip "找不到 python"
else
  # overnight-runner 零依赖，用系统 python 即可
  if "$PY" overnight-runner/tests/test_units.py > /tmp/orn-units.log 2>&1; then
    tail -1 /tmp/orn-units.log | while IFS= read -r line; do printf '  \033[32m✔\033[0m 单元测试 %s\n' "$line"; done
    PASSED=$((PASSED + 1))
  else
    sed 's/^/  /' /tmp/orn-units.log
    bad "单元测试"
  fi
  if "$PY" overnight-runner/tests/test_smoke.py > /tmp/orn-smoke.log 2>&1; then
    tail -1 /tmp/orn-smoke.log | while IFS= read -r line; do printf '  \033[32m✔\033[0m 冒烟测试 %s\n' "$line"; done
    PASSED=$((PASSED + 1))
  else
    sed 's/^/  /' /tmp/orn-smoke.log
    bad "冒烟测试"
  fi
fi

# ── 11. overnight-runner 队列布局 / 迁移 / 决策默认值 ───────────────
head_ "11. overnight-runner 队列布局与决策默认值"
if [ "$FAST" -eq 1 ]; then
  skip "--fast 跳过"
elif [ -z "$PY" ]; then
  skip "找不到 python"
else
  "$PY" - <<'PYEOF'
import pathlib, sys, tempfile

sys.path.insert(0, str(pathlib.Path('overnight-runner').resolve()))
from overnight_runner import yaml_lite
from overnight_runner.config import (
    DECISION_MODES,
    DECISION_MODE_ATTENDED,
    DECISION_MODE_UNATTENDED,
    DecisionConfig,
    migrate_legacy_queue,
    queue_names,
    queue_paths,
)
from overnight_runner.queue import load_queue_defs

bad = []

# 11.1 队列目录结构：常量与实际路径一致
paths = queue_paths(pathlib.Path('/tmp/x'), 'alice')
expect = {
    'dir': '.overnight-runner/queue/alice',
    'config': '.overnight-runner/queue/alice/queue.yaml',
    'state': '.overnight-runner/queue/alice/state.json',
    'logs': '.overnight-runner/queue/alice/logs',
    'decisions': '.overnight-runner/queue/alice/decisions.jsonl',
    'lock': '.overnight-runner/queue/alice/.lock',
}
for attr, want in expect.items():
    got = getattr(paths, attr).as_posix().replace('/tmp/x/', '')
    if got != want:
        print(f'  \033[31m✘\033[0m 队列路径 {attr}: {got} ≠ {want}')
        bad.append(attr)

# 11.2 决策模式默认值与合法取值
cfg = DecisionConfig()
if cfg.mode != DECISION_MODE_ATTENDED:
    print(f'  \033[31m✘\033[0m 默认决策模式 {cfg.mode} ≠ attended')
    bad.append('mode')
if cfg.timeout_sec != 600:
    print(f'  \033[31m✘\033[0m 默认决策窗口 {cfg.timeout_sec}s ≠ 600s')
    bad.append('timeout')
if cfg.resume != 'session':
    print(f'  \033[31m✘\033[0m 默认续跑方式 {cfg.resume} ≠ session')
    bad.append('resume')
if set(DECISION_MODES) != {DECISION_MODE_ATTENDED, DECISION_MODE_UNATTENDED}:
    print(f'  \033[31m✘\033[0m 决策模式取值应为 attended/unattended，实际 {DECISION_MODES}')
    bad.append('modes')

# 11.3 迁移幂等：连跑两次，队列不丢不重
with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp)
    (root / '.overnight-runner').mkdir(parents=True)
    (root / 'overnight-runner.yaml').write_text(
        yaml_lite.dumps({
            'runner': {'agent': {'command': 'opencode', 'args': ['run']}},
            'queue': [{'id': 't1', 'plan': 'docs/plans/p1.md'}],
        }),
        encoding='utf-8',
    )
    migrate_legacy_queue(root)
    migrate_legacy_queue(root)
    p = queue_paths(root, 'default')
    defs = load_queue_defs(p)
    if len(defs) != 1 or defs[0].get('id') != 't1':
        print(f'  \033[31m✘\033[0m 迁移后队列内容不对: {defs}')
        bad.append('migrate')
    if queue_names(root) != ['default']:
        print(f'  \033[31m✘\033[0m 迁移后队列名不对: {queue_names(root)}')
        bad.append('migrate-names')
    cfg_path = root / '.overnight-runner' / 'overnight-runner.yaml'
    if not cfg_path.exists():
        print('  \033[31m✘\033[0m 迁移后 overnight-runner.yaml 未进入 .overnight-runner/')
        bad.append('migrate-cfg-path')
    elif (root / 'overnight-runner.yaml').exists():
        print('  \033[31m✘\033[0m 迁移后根目录仍留有 overnight-runner.yaml')
        bad.append('migrate-root-left')
    else:
        raw = yaml_lite.loads(cfg_path.read_text(encoding='utf-8'))
        if raw.get('queue'):
            print('  \033[31m✘\033[0m 迁移后配置的 queue 段没清空')
            bad.append('migrate-clear')

# 11.4 .gitignore 排除了队列运行时产物
gi = pathlib.Path('.gitignore').read_text(encoding='utf-8')
for pat in ('**/.overnight-runner/queue/*/state.json',
            '**/.overnight-runner/queue/*/logs/',
            '**/.overnight-runner/queue/*/.lock'):
    if pat not in gi:
        print(f'  \033[31m✘\033[0m .gitignore 缺 {pat}')
        bad.append('gitignore')

if not bad:
    print('  \033[32m✔\033[0m 队列布局、迁移幂等、决策默认值一致')
sys.exit(1 if bad else 0)
PYEOF
  if [ $? -eq 0 ]; then PASSED=$((PASSED + 1)); else FAILED=$((FAILED + 1)); fi
fi

# ── 12. agents-workflow-engine ────────────────────────────────────
head_ "12. agents-workflow-engine 测试"
if [ -z "$PY" ]; then
  skip "找不到 python"
else
  if "$PY" agents-workflow-engine/tests/test_units.py > /tmp/awe-units.log 2>&1 && grep -q '^OK$' /tmp/awe-units.log; then
    grep '^Ran ' /tmp/awe-units.log | while IFS= read -r line; do printf '  \033[32m✔\033[0m %s\n' "$line"; done
    PASSED=$((PASSED + 1))
  else
    sed 's/^/  /' /tmp/awe-units.log
    bad "单元测试"
  fi
fi

# 版本号：version.py 是唯一事实源，CHANGELOG 最新一节必须与之一致
VER_ENGINE="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' agents-workflow-engine/agents_workflow_engine/version.py 2>/dev/null)"
VER_LOG="$(grep -m1 '^## \[' agents-workflow-engine/CHANGELOG.md 2>/dev/null | sed 's/^## \[\([^]]*\)\].*/\1/')"
if [ -n "$VER_ENGINE" ] && [ "$VER_ENGINE" = "$VER_LOG" ]; then
  ok "引擎版本一致: $VER_ENGINE"
else
  bad "引擎版本不一致: version.py=${VER_ENGINE:-空} CHANGELOG=${VER_LOG:-空}"
fi

# ── 13. 版本与安装清单 ─────────────────────────────────────────────
head_ "13. 版本与安装清单"

# 仓库根 VERSION 是套件版本的唯一事实源，CHANGELOG 最新一节必须与之一致
VER_SUITE="$(sed -n '1s/[[:space:]]*$//;1p' VERSION 2>/dev/null)"
VER_SUITE_LOG="$(grep -m1 '^## \[' CHANGELOG.md 2>/dev/null | sed 's/^## \[\([^]]*\)\].*/\1/')"
if [ -n "$VER_SUITE" ] && [ "$VER_SUITE" = "$VER_SUITE_LOG" ]; then
  ok "套件版本一致: $VER_SUITE"
else
  bad "套件版本不一致: VERSION=${VER_SUITE:-空} CHANGELOG=${VER_SUITE_LOG:-空}"
fi

# 每个模块装进目标项目时写一份 .agents/harness/<模块>.json；这里比对「已安装副本 ↔ 源码」
manifest_field() {
  sed -n "s/.*\"$2\": *\"\([^\"]*\)\".*/\1/p" "$1" 2>/dev/null | head -1
}
manifest_count=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  manifest_count=$((manifest_count + 1))
  module="$(basename "$f" .json)"
  got="$(manifest_field "$f" suite)"
  if [ "$got" = "$VER_SUITE" ]; then
    ok "清单 $module 套件 $got"
  else
    bad "清单 $module 套件 ${got:-空} ≠ 源码 ${VER_SUITE}（重跑该模块安装器）"
  fi
done < <(find example-project/.agents/harness -name "*.json" 2>/dev/null | sort)
if [ "$manifest_count" -eq 0 ]; then
  skip "example-project 还没有安装清单（跑完安装器就会出现）"
fi

# 自带版本号的模块：清单里的 version 必须等于它自己的版本源
check_manifest_version() {
  f="example-project/.agents/harness/$1.json"
  [ -f "$f" ] || return 0
  got="$(manifest_field "$f" version)"
  if [ "$got" = "$2" ]; then
    ok "清单 $1 版本 $got"
  else
    bad "清单 $1 版本 ${got:-空} ≠ 源码 ${2:-空}"
  fi
}
VER_RUNNER="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' overnight-runner/overnight_runner/__init__.py 2>/dev/null)"
check_manifest_version overnight-runner "$VER_RUNNER"
check_manifest_version agents-workflow-engine "$VER_ENGINE"

# ── 汇总 ───────────────────────────────────────────────────────────
printf '\n\033[1m%s\033[0m\n' "────────────────────────────"
if [ "$FAILED" -eq 0 ]; then
  printf '\033[32m全部通过\033[0m（%s 项）\n' "$PASSED"
  exit 0
fi
printf '\033[31m失败 %s 项\033[0m（通过 %s 项）\n' "$FAILED" "$PASSED"
exit 1
