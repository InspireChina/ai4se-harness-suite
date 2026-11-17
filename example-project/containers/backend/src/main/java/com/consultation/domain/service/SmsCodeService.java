package com.consultation.domain.service;

import com.consultation.domain.aggregate.SmsVerificationCode;
import com.consultation.domain.repository.SmsVerificationCodeRepository;

import java.security.SecureRandom;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.UUID;

/**
 * 短信验证码领域服务：签发、校验、TTL、连续失败作废、重发限流。
 *
 * <p>纯 Java（不依赖 Spring），由 infrastructure 配置类注册为 Bean。</p>
 */
public class SmsCodeService {

    /** 验证码有效期。 */
    public static final Duration DEFAULT_TTL = Duration.ofMinutes(5);
    /** 同一手机号重发间隔。 */
    public static final Duration DEFAULT_RESEND_INTERVAL = Duration.ofSeconds(60);
    /** 连续失败上限，超过即作废（R-CREATE-002）。 */
    public static final int DEFAULT_MAX_FAILURES = 5;

    private static final SecureRandom RANDOM = new SecureRandom();
    private static final int CODE_BOUND = 1_000_000;

    private final SmsVerificationCodeRepository repository;
    private final SmsSender smsSender;
    private final PhoneCrypto phoneCrypto;
    private final Duration ttl;
    private final Duration resendInterval;
    private final int maxFailures;
    private final Clock clock;

    public SmsCodeService(SmsVerificationCodeRepository repository, SmsSender smsSender, PhoneCrypto phoneCrypto) {
        this(repository, smsSender, phoneCrypto, DEFAULT_TTL, DEFAULT_RESEND_INTERVAL, DEFAULT_MAX_FAILURES,
                Clock.systemUTC());
    }

    public SmsCodeService(SmsVerificationCodeRepository repository, SmsSender smsSender, PhoneCrypto phoneCrypto,
                          Duration ttl, Duration resendInterval, int maxFailures, Clock clock) {
        this.repository = repository;
        this.smsSender = smsSender;
        this.phoneCrypto = phoneCrypto;
        this.ttl = ttl;
        this.resendInterval = resendInterval;
        this.maxFailures = maxFailures;
        this.clock = clock;
    }

    /**
     * 签发验证码并发送。
     *
     * @param phone     明文手机号（用于发送）
     * @param phoneHash 手机号摘要（用于查询）
     */
    public void issue(String phone, String phoneHash) {
        Instant now = clock.instant();
        repository.findLatestByPhoneHash(phoneHash).ifPresent(latest -> {
            if (now.isBefore(latest.getCreatedAt().plus(resendInterval))) {
                throw new IllegalStateException("验证码发送过于频繁，请稍后再试");
            }
        });

        String code = randomCode();
        String delivered = smsSender.send(phone, code);
        SmsVerificationCode entity = SmsVerificationCode.builder()
                .id(UUID.randomUUID().toString())
                .phoneHash(phoneHash)
                .codeHash(hashCode(phoneHash, delivered))
                .expiresAt(now.plus(ttl))
                .failCount(0)
                .createdAt(now)
                .build();
        repository.save(entity);
    }

    /**
     * 校验验证码；失败抛 IllegalArgumentException（400），连续失败超限后作废。
     */
    public void verify(String phoneHash, String code) {
        Instant now = clock.instant();
        SmsVerificationCode entity = repository.findLatestByPhoneHash(phoneHash)
                .orElseThrow(() -> new IllegalArgumentException("验证码不存在或已过期"));
        if (entity.isUsed()) {
            throw new IllegalArgumentException("验证码已使用，请重新获取");
        }
        if (entity.isExpired(now)) {
            throw new IllegalArgumentException("验证码已过期，请重新获取");
        }
        if (!entity.matches(hashCode(phoneHash, code))) {
            SmsVerificationCode failed = entity.recordFailure();
            if (failed.getFailCount() >= maxFailures) {
                repository.save(failed.invalidate(now));
                throw new IllegalArgumentException("验证码连续错误次数过多，已作废");
            }
            repository.save(failed);
            throw new IllegalArgumentException("验证码错误");
        }
        repository.save(entity.invalidate(now));
    }

    private String hashCode(String phoneHash, String code) {
        return phoneCrypto.hash("sms:" + phoneHash + ":" + code);
    }

    private String randomCode() {
        return String.format("%06d", RANDOM.nextInt(CODE_BOUND));
    }
}
