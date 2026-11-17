# E2E 测试分层

本目录下的 E2E 用例按 **归属** 分成两层。两层的验收效力完全不同，不要混。

```
tests/
├── qa/     # QA 验收用例（自动化实现）—— 合并闸门
└── dev/    # 开发自测用例（自动化实现）—— 仅供开发反馈
```

| | `qa/` | `dev/` |
|---|---|---|
| 用例来源 | `docs/test-cases/e2e-cases/test-cases.md` 的 QA 验收用例 | 开发按 Plan 自定 |
| 编号 | `TC-xxx` | 无编号，标题自解释 |
| 谁判定 | QA | 开发本人 |
| 合并闸门 | **是** —— 不通过不能合并 | 否 —— 挂了不阻塞别人，但必须自己修 |
| 关注点 | 需求规格有没有被实现 | 我这次改的东西有没有被我改坏 |

## 约定

- `qa/` 下的每个 `test()` 都要能对应到 `docs/test-cases/e2e-cases/test-cases.md` 里的一条用例（编号一致）。
- `dev/` 下的用例只服务于开发期的快速反馈，**不能** 作为验收依据。
- 新增 QA 用例时，**先**在 `docs/test-cases/e2e-cases/test-cases.md` 里写文本用例，再写自动化。
- 自动化实现可以由开发代写，但 **用例的判定权归 QA**。

## 运行

```bash
npm test          # 全部（qa + dev）
npm run test:qa   # 只跑 QA 验收用例
npm run test:dev  # 只跑开发自测用例
```
