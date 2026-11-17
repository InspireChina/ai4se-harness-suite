package com.consultation.infrastructure.config;

import com.consultation.domain.aggregate.Account;
import com.consultation.domain.repository.AccountRepository;
import com.consultation.domain.service.PasswordService;
import com.consultation.domain.service.PhoneCrypto;
import com.consultation.domain.vo.PhoneNumber;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

/**
 * 平台管理员账号种子（R-COMMON-001：ADMIN 只由平台分配）。
 *
 * <p>运行时创建而非写死在 data.sql：管理员手机号需要用当前环境的加密密钥落密文。</p>
 */
@Slf4j
@Component
public class AccountSeedInitializer implements ApplicationRunner {

    private final AccountRepository accountRepository;
    private final PhoneCrypto phoneCrypto;
    private final PasswordService passwordService;

    private final boolean enabled;
    private final String adminPhone;
    private final String adminPassword;

    public AccountSeedInitializer(AccountRepository accountRepository,
                                  PhoneCrypto phoneCrypto,
                                  PasswordService passwordService,
                                  @Value("${seed.admin.enabled:true}") boolean enabled,
                                  @Value("${seed.admin.phone:13900000000}") String adminPhone,
                                  @Value("${seed.admin.password:Admin@12345}") String adminPassword) {
        this.accountRepository = accountRepository;
        this.phoneCrypto = phoneCrypto;
        this.passwordService = passwordService;
        this.enabled = enabled;
        this.adminPhone = adminPhone;
        this.adminPassword = adminPassword;
    }

    @Override
    public void run(ApplicationArguments args) {
        ensureAdminAccount();
    }

    /**
     * 若管理员账号不存在则创建（幂等）。返回新建的账号，已存在时返回 null。
     */
    @Transactional
    public Account ensureAdminAccount() {
        if (!enabled) {
            return null;
        }
        String phone = PhoneNumber.of(adminPhone).value();
        String phoneHash = phoneCrypto.hash(phone);
        if (accountRepository.findByPhoneHash(phoneHash).isPresent()) {
            return null;
        }
        Account admin = Account.createAdmin(
                UUID.randomUUID().toString(),
                phoneHash,
                phoneCrypto.encrypt(phone),
                passwordService.encode(adminPassword),
                Instant.now());
        accountRepository.save(admin);
        log.info("已创建平台管理员账号：{}", adminPhone);
        return admin;
    }
}
