# 测试用例（`docs/test-cases/`）

本目录集中存放 **文本用例基线**（与自动化目录 `e2e/tests/` 分离）。

| 子目录 | 归属 | 内容 |
|---|---|---|
| `e2e-cases/` | **QA 测试** | E2E 验收用例文本基线（`TC-xxx`），合并闸门 |
| `manual-cases/` | **QA 测试** | 需人工执行的用例（`TC-Mxx`） |
| `smoking-cases/` | **QA 测试** | 发版前冒烟用例（`TC-Sxx`，≤ 5 分钟） |
| `dev-self-cases/` | **开发自测** | 开发自测场景清单（可选文本索引；实现仍在源码旁 / `e2e/tests/dev/`） |

> QA 三目录：定义权与判定权归 QA。  
> `dev-self-cases/`：对开发本人负责，**不是**合并闸门。
