# 数据库规格

> 当前已实现 ACC（账号与个人中心）的业务表。  
> 其余 feature 按 `docs/features/iteration1/` 继续通过 Flyway 新增表，并同步本文档。

## 迁移

- 目录：`containers/backend/src/main/resources/db/migration/`
- 回滚脚本目录：`containers/backend/src/main/resources/db/rollback/`（Flyway 不自动执行，人工按需回滚）

| 版本 | 脚本 | 说明 |
|---|---|---|
| 20261117 | `V20261117__acc_account.sql` | ACC 账号与个人中心（5 张表） |

## 表清单

### account（账号）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | VARCHAR(64) | PK | UUID 字符串 |
| phone_hash | VARCHAR(64) | NOT NULL，UNIQUE(`uk_account_phone_hash`) | 手机号摘要（HMAC-SHA256，带密钥），唯一登录标识 |
| phone_cipher | VARCHAR(512) | NOT NULL | 手机号密文（AES-256-GCM），仅本人可解密展示 |
| roles_json | VARCHAR(128) | NOT NULL | 角色 JSON 数组，如 `["USER"]` |
| status | VARCHAR(32) | NOT NULL | `ACTIVE` / `DISABLED` |
| phone_verified_at | DATETIME(3) | NOT NULL | 最近一次手机号验证时间 |
| last_login_at | DATETIME(3) | NULL | 最近登录时间 |
| disabled_reason | VARCHAR(200) | NULL | 禁用原因（禁用时必填） |
| token_version | INT | NOT NULL DEFAULT 0 | 会话版本，禁用/启用时 +1，使旧 JWT 失效 |
| password_hash | VARCHAR(255) | NULL | 仅 ADMIN 账号使用（BCrypt） |
| created_at / updated_at | DATETIME(3) | NOT NULL | 创建/更新时间 |

### user_profile（用户资料）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| account_id | VARCHAR(64) | PK，FK→account(id) | 账号 ID |
| nickname | VARCHAR(30) | NOT NULL | 昵称（2~30 字符） |
| avatar_url | VARCHAR(500) | NULL | 头像地址 |
| email | VARCHAR(254) | NULL | 邮箱 |
| city_code | VARCHAR(20) | NULL | 城市编码 |
| locale | VARCHAR(16) | NOT NULL DEFAULT 'zh-CN' | 语言 |
| updated_at | DATETIME(3) | NOT NULL | 资料更新时间 |

### favorite_consultant（收藏咨询师）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | VARCHAR(64) | PK | 收藏记录 ID |
| account_id | VARCHAR(64) | NOT NULL，FK→account(id)，索引 `idx_fav_account` | 收藏人 |
| consultant_id | VARCHAR(64) | NOT NULL | 被收藏咨询师（与 account_id 组成唯一键 `uk_fav_account_consultant`） |
| created_at | DATETIME(3) | NOT NULL | 收藏时间 |

### agreement_consent（协议同意记录）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | VARCHAR(64) | PK | 记录 ID（不可变、不可物理删除） |
| account_id | VARCHAR(64) | NOT NULL，FK→account(id)，索引 `idx_consent_account` | 同意人 |
| agreement_type | VARCHAR(32) | NOT NULL | `SERVICE` / `PRIVACY`（对外小写 `service` / `privacy`） |
| agreement_version | VARCHAR(20) | NOT NULL | 协议版本 |
| consented_at | DATETIME(3) | NOT NULL | 同意时间 |
| source_ip | VARCHAR(45) | NOT NULL | 来源 IP |

唯一键 `uk_consent_account_type_ver(account_id, agreement_type, agreement_version)` 保证同版本幂等。

### sms_verification_code（短信验证码）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | VARCHAR(64) | PK | 记录 ID |
| phone_hash | VARCHAR(64) | NOT NULL，索引 `idx_sms_phone_created(phone_hash, created_at)` | 手机号摘要 |
| code_hash | VARCHAR(64) | NOT NULL | 验证码摘要（不存明文） |
| expires_at | DATETIME(3) | NOT NULL | 过期时间（默认 5 分钟） |
| fail_count | INT | NOT NULL DEFAULT 0 | 连续失败次数（达 5 次作废） |
| used_at | DATETIME(3) | NULL | 使用 / 作废时间 |
| created_at | DATETIME(3) | NOT NULL | 创建时间（重发间隔按此判断） |

## 约定

- 字符集 `utf8mb4` / 排序 `utf8mb4_bin`，引擎 InnoDB，表名单数小写下划线。
- 时间统一按 `Asia/Shanghai` 存储（`DATETIME(3)`），领域层用 `Instant`，转换见 `TimeConverter`。
- 测试库不用 Flyway：改用 `src/test/resources/schema.sql`（结构）与 `data.sql`（种子）。
  管理员种子账号由 `AccountSeedInitializer` 在运行时创建（密文与部署环境密钥相关）。
