-- 回滚脚本：撤销 V20261117__acc_account.sql
-- 用法：mysql -u<user> -p<pass> <db> < V20261117__acc_account_rollback.sql
-- 说明：ACC 为首个业务迁移，无历史业务数据；回滚即删表。
-- 顺序：先删子表（外键依赖），再删主表。

DROP TABLE IF EXISTS sms_verification_code;
DROP TABLE IF EXISTS agreement_consent;
DROP TABLE IF EXISTS favorite_consultant;
DROP TABLE IF EXISTS user_profile;
DROP TABLE IF EXISTS account;
