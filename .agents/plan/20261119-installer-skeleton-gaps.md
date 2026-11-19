# Plan：补齐 harness-installer 的骨架缺口（路径口径 / standards 骨架 / 相对路径模式）

> 日期：2026-11-19
> 状态：**已完成**（方案 B）
> 范围：只改 `harness-installer/`（模板 + 脚本 + 文档）与 `.agents/verify.sh`；不动 `agile-team-sdd/`、不动 `example-project/`、不动 `overnight-runner/`

## 背景

把整套 harness 首次装到 `poc-company-a`（Spring Boot 3 + Vue 3，`PATH_MODE=relative`）时暴露三个缺口，
都需要人工兜底才能交付可用骨架。本方案把它们在模板里修掉，避免下一个项目重复兜底。

### 现状问题（实测证据）

1. **测试用例路径口径不一致**
   `templates/AGENTS.md.template` 把手动/冒烟用例写成 `{{DOCS_DIR}}/manual-cases/`、`{{DOCS_DIR}}/smoking-cases/`，
   但 `templates/docs/` 实际建在 `docs/test-cases/{manual,smoking}-cases/`。
   出现位置：§10「QA 测试要求」四类产物、§13 目录树末尾三行、§13 备注。
   安装到 poc-company-a 后 3 处全部指向不存在的目录，已人工修正。

2. **§13 声明的 standards 文件不存在**
   §13 目录树列了 `architecture.md / naming.md / security.md / api-design.md / layers.md / db.md / error.md / test.md`，
   但 `templates/docs/standards/` 只有 `README.md`、`adr.md`、`templates/`。
   结果是 `AGENTS.md` 里 `docs/standards/test.md` 这类引用全是死链，新项目一装就"声明与实物不符"。
   poc-company-a 是人工从 `example-project/docs/standards/` 拷贝并去掉业务痕迹补齐的。

3. **`init-harness.sh` 不支持相对路径**
   `scripts/init-harness.sh:102-124` 把 `{{PROJECT_ROOT}}/...` 拼进所有占位符，产物里必然写死安装机绝对路径；
   而同一次安装里 `agile-team-sdd/install.sh` 支持 `PATH_MODE=relative`。两者并存时
   `AGENTS.md` 用绝对路径、`.agents/skills/` 用相对路径，互相矛盾；也违反 §6「不写绝对路径到产物」。

## 改动 1：AGENTS.md 模板的测试用例路径口径

文件：`harness-installer/templates/AGENTS.md.template`

- §10「QA 测试要求」第 3 条：手动用例 → `{{DOCS_DIR}}/test-cases/manual-cases/`，冒烟用例 → `{{DOCS_DIR}}/test-cases/smoking-cases/`
- §13 目录树：把 `e2e-cases/ manual-cases/ smoking-cases/` 三行移到 `test-cases/` 节点下，并补 `dev-self-cases/`
- §13 备注：`{{DOCS_DIR}}/` → `{{DOCS_DIR}}/test-cases/`

不新增占位符（`{{DEV_SELF_CASES_DIR}}` 等已登记在 `placeholders.md`，但 AGENTS.md 模板用相对写法即可，不需要全部引入）。

## 改动 2：standards 骨架与 §13 声明对齐（请选一个方案）

- **方案 A（收敛声明）**：§13 树里的 standards 只保留 `README.md` / `adr.md` / `templates/`，
  并注明「其余规范按需创建」。改动量最小，但新项目拿不到任何规范基线。
- **方案 B（补齐必用四份，推荐）**：新增
  `templates/docs/standards/{architecture,layers,naming,test}.md`，
  写成 **通用版**（不写死业务名、包名、数据库选型，未定项留 `TODO`）；
  §13 树的 `security.md / api-design.md / db.md / error.md` 标注「按需创建」。
- **方案 C（全量补齐八份）**：B 加上 security / api-design / db / error。模板维护成本最高，
  且这几份和具体技术栈强绑定，容易写成"看起来是规范、实际没定"。

推荐 **B**：

- `test.md` 与 `layers.md` 是 `dev-build` / `dev-code-review` / `qa-*` 直接读的规范，缺了流程就会各自发挥；
- `naming.md` 是代码评审的判定依据；
- `architecture.md` 是 `tl-arch-plan` 的落点说明；
- 其余四份强依赖选型（JWT/ORM/错误码体系），空骨架反而制造假权威。

配套：`templates/docs/standards/README.md` 的索引表要标注「预置 / 按需创建」两栏，避免又出现"表里有、盘上没有"。

## 改动 3：`init-harness.sh` 支持 `PATH_MODE`

文件：`harness-installer/scripts/init-harness.sh`

- 新增 `PATH_MODE="${PATH_MODE:-absolute}"`，语义与 `agile-team-sdd/install.sh` 完全一致：
  `relative` 时项目内路径渲染成相对路径，`{{PROJECT_ROOT}}` 渲染为 `.`
- 抽出 `proj_path()`（与 SDD 安装器同实现），PAIRS 全部改走它
- `--dry-run` / 正常输出的头部增加 `路径模式: absolute|relative` 一行
- 不改：结构探测、幂等语义（默认跳过、`--force` 覆盖）、写入的文件集合、`opencode.jsonc` 处理

向后兼容：默认仍 `absolute`，既有调用方零影响。

## 改动 4（顺带，已执行）

- 删除根 `README.md` 末尾误提交的 `# poc-company-a` 一行（`README.md:221`，11-19 11:38 误入）。

## 验证

1. `bash -n harness-installer/scripts/init-harness.sh`
2. 两种模式各在临时目录装一次：
   - `PATH_MODE=relative`：`AGENTS.md` 里 `grep -c "$TMPDIR项目路径"` 必须为 0
   - 默认 `absolute`：行为与改动前一致（`--dry-run` 输出 diff 为空）
3. 断言骨架与声明一致：脚本提取 `AGENTS.md` 渲染结果里出现的 `docs/**` 路径（排除 `facts/` as-built 产物），逐个检查文件是否存在
4. `./.agents/verify.sh` 全绿
5. 文档同步：`harness-installer/README.md`（脚本行为 + 文件清单）、`harness-installer/SKILL.md`（参数表加 `PATH_MODE`）；
   根 `README.md` 的快速开始补一句 `PATH_MODE=relative` 的用法

## 回归风险

- 改动 2 若选 B/C，新增的是**模板文件**，`verify.sh` 的"清单 ↔ 模板 ↔ 已安装"检查不涉及 docs 模板，风险低
- 改动 3 触碰渲染主路径：以"默认 absolute 行为不变"为硬约束，用第 2 项的 diff 断言守住
- `example-project/docs/standards/` 不动，避免参考实现被模板反向污染

## 实施结果（2026-11-19）

选定 **方案 B**，已全部实现：

| 改动 | 落地内容 |
|---|---|
| 1 | `AGENTS.md.template` §10 四类产物改用 `{{MANUAL_CASES_DIR}}` / `{{SMOKING_CASES_DIR}}`；§13 树把三个用例目录挂到 `test-cases/` 并补 `dev-self-cases/`；备注改 `{{DOCS_DIR}}/test-cases/` |
| 2 | 新增 `templates/docs/standards/{architecture,layers,naming,test}.md`（通用版，不绑技术栈）；§13 树标「预置 / 按需创建」；`standards/README.md` 索引表加状态列 |
| 3 | `init-harness.sh` 支持 `PATH_MODE`（`proj_path()` 统一展开），新增 `TEST_CASES_DIR / MANUAL_CASES_DIR / SMOKING_CASES_DIR / DEV_SELF_CASES_DIR / RELEASES_DIR` 五个占位符的替换；输出与 `--help` 标注路径模式；非法值报错退出 |
| 4 | 根 `README.md` 尾行 `# poc-company-a` 已删 |
| 5 | 同步 `harness-installer/README.md`、`harness-installer/SKILL.md`、根 `README.md` 快速开始（`PATH_MODE=relative` 两步同开） |

验证增强（防回退）：

- `verify.sh` 检查 7：增加"harness-installer 模板里的占位符必须能被 `init-harness.sh` 替换"
- `verify.sh` 新增检查 9.1：临时目录分别按 abs / rel 装一次，断言无残留占位符、rel 不泄漏绝对路径、`AGENTS.md` 声明的 `docs/` 路径都真实存在

验证结果：

- `bash -n` 通过；HEAD 版与新版在同样绝对模式下 `diff -r` 只差项目名与本次修的内容（无路径格式变化）
- 相对模式：产物里 0 个安装机绝对路径；未替换占位符 0
- `./.agents/verify.sh`：**68 项全部通过**

遗留（不在本次范围）：

- `poc-company-a` 已装产物是人工补齐版（standards 十份、architecture/test/db 按项目改过）；
  将来对它跑 `install.sh --force` 会用通用模板覆盖其中四份，需要人工合并
- `example-project/docs/standards/` 未同步这套通用版（它是参考实现，自带完整版属正常）