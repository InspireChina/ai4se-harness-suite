-- 测试种子数据
-- 平台管理员账号（手机号 13900000000 / 密码 Admin@12345）由
-- com.consultation.infrastructure.config.AccountSeedInitializer 在运行时创建：
-- 管理员手机号需要用当前环境的加密密钥落密文，无法固化为静态 SQL。
-- 每个用例前由 ResetDbService 清库并重建该管理员。
--
-- 「可展示咨询师」白名单（stub-consultant-001）配置在 application.yml 的
-- consultant.displayable-ids，无需数据库行。

SELECT 1;
