-- 测试用库表结构（与 Flyway V20261117__acc_account.sql 保持一致）
-- Flyway 在测试中禁用，改用本脚本初始化。

CREATE TABLE IF NOT EXISTS account (
  id                VARCHAR(64)  NOT NULL PRIMARY KEY,
  phone_hash        VARCHAR(64)  NOT NULL,
  phone_cipher      VARCHAR(512) NOT NULL,
  roles_json        VARCHAR(128) NOT NULL COMMENT 'JSON array e.g. ["USER"]',
  status            VARCHAR(32)  NOT NULL,
  phone_verified_at DATETIME(3)  NOT NULL,
  last_login_at     DATETIME(3)  NULL,
  disabled_reason   VARCHAR(200) NULL,
  token_version     INT          NOT NULL DEFAULT 0,
  password_hash     VARCHAR(255) NULL COMMENT 'ADMIN only',
  created_at        DATETIME(3)  NOT NULL,
  updated_at        DATETIME(3)  NOT NULL,
  UNIQUE KEY uk_account_phone_hash (phone_hash)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_bin;

CREATE TABLE IF NOT EXISTS user_profile (
  account_id   VARCHAR(64)  NOT NULL PRIMARY KEY,
  nickname     VARCHAR(30)  NOT NULL,
  avatar_url   VARCHAR(500) NULL,
  email        VARCHAR(254) NULL,
  city_code    VARCHAR(20)  NULL,
  locale       VARCHAR(16)  NOT NULL DEFAULT 'zh-CN',
  updated_at   DATETIME(3)  NOT NULL,
  CONSTRAINT fk_profile_account FOREIGN KEY (account_id) REFERENCES account(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_bin;

CREATE TABLE IF NOT EXISTS favorite_consultant (
  id             VARCHAR(64) NOT NULL PRIMARY KEY,
  account_id     VARCHAR(64) NOT NULL,
  consultant_id  VARCHAR(64) NOT NULL,
  created_at     DATETIME(3) NOT NULL,
  UNIQUE KEY uk_fav_account_consultant (account_id, consultant_id),
  KEY idx_fav_account (account_id),
  CONSTRAINT fk_fav_account FOREIGN KEY (account_id) REFERENCES account(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_bin;

CREATE TABLE IF NOT EXISTS agreement_consent (
  id                 VARCHAR(64)  NOT NULL PRIMARY KEY,
  account_id         VARCHAR(64)  NOT NULL,
  agreement_type     VARCHAR(32)  NOT NULL,
  agreement_version  VARCHAR(20)  NOT NULL,
  consented_at       DATETIME(3)  NOT NULL,
  source_ip          VARCHAR(45)  NOT NULL,
  KEY idx_consent_account (account_id),
  UNIQUE KEY uk_consent_account_type_ver (account_id, agreement_type, agreement_version),
  CONSTRAINT fk_consent_account FOREIGN KEY (account_id) REFERENCES account(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_bin;

CREATE TABLE IF NOT EXISTS sms_verification_code (
  id            VARCHAR(64)  NOT NULL PRIMARY KEY,
  phone_hash    VARCHAR(64)  NOT NULL,
  code_hash     VARCHAR(64)  NOT NULL,
  expires_at    DATETIME(3)  NOT NULL,
  fail_count    INT          NOT NULL DEFAULT 0,
  used_at       DATETIME(3)  NULL,
  created_at    DATETIME(3)  NOT NULL,
  KEY idx_sms_phone_created (phone_hash, created_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_bin;
