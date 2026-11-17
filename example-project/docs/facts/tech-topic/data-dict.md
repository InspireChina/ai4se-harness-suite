# 数据字典

> 框架类型保留（`Description` / `DataDictionaryType` / `DataDictionaryUtil`）。  
> ACC 已注册 `AccDataDictionaryType`（`domain/datadictionary/AccDataDictionaryType.java`）。

## 当前注册字典类型

| 类型 | 说明 | 枚举来源 |
|---|---|---|
| `AccDataDictionaryType.ACCOUNT_STATUS` | 账号状态 | `AccountStatus`（ACTIVE / DISABLED） |
| `AccDataDictionaryType.ACCOUNT_ROLE` | 账号角色 | `AccountRole`（USER / CONSULTANT / ADMIN） |
| `AccDataDictionaryType.AGREEMENT_TYPE` | 协议类型 | `AgreementType`（service / privacy） |

## 新增枚举的约定

1. 枚举放在 `domain/vo/`，实现 `Description`（`getCode()` / `getDescription()`）。
2. 在 `AccDataDictionaryType`（或后续 feature 的字典类型）中登记。
3. 回写本文档的「当前注册字典类型」表。
