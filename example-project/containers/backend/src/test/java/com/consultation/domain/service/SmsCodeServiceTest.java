package com.consultation.domain.service;

import com.consultation.domain.aggregate.SmsVerificationCode;
import com.consultation.domain.service.PhoneCrypto;
import com.consultation.domain.service.SmsSender;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SmsCodeServiceTest {

    private static final Instant NOW = Instant.parse("2026-11-17T10:00:00Z");
    private static final String PHONE = "13800138000";
    private static final String PHONE_HASH = "phone-hash";

    private final FakeSmsVerificationCodeRepository repository = new FakeSmsVerificationCodeRepository();
    private final CapturingSmsSender sender = new CapturingSmsSender();
    private final PhoneCrypto phoneCrypto = new PlainHashCrypto();

    private SmsCodeService service(Duration ttl, Duration resendInterval) {
        return new SmsCodeService(repository, sender, phoneCrypto, ttl, resendInterval, 5,
                Clock.fixed(NOW, ZoneOffset.UTC));
    }

    @Test
    void should_issue_code_and_store_hashed_value() {
        service(Duration.ofMinutes(5), Duration.ofSeconds(60)).issue(PHONE, PHONE_HASH);

        assertNotNull(sender.sentCode());
        assertNotNull(repository.latest());
        assertTrue(repository.latest().getCodeHash().contains(sender.sentCode()));
        assertEquals(0, repository.latest().getFailCount());
        assertEquals(NOW.plus(Duration.ofMinutes(5)), repository.latest().getExpiresAt());
    }

    @Test
    void should_reject_resend_within_interval() {
        SmsCodeService service = service(Duration.ofMinutes(5), Duration.ofSeconds(60));
        service.issue(PHONE, PHONE_HASH);

        IllegalStateException error = assertThrows(IllegalStateException.class,
                () -> service.issue(PHONE, PHONE_HASH));
        assertTrue(error.getMessage().contains("频繁"));
    }

    @Test
    void should_allow_resend_after_interval() {
        SmsCodeService service = service(Duration.ofMinutes(5), Duration.ZERO);
        service.issue(PHONE, PHONE_HASH);
        service.issue(PHONE, PHONE_HASH);

        assertEquals(2, sender.sendCount);
    }

    @Test
    void should_verify_code_with_correct_value() {
        SmsCodeService service = service(Duration.ofMinutes(5), Duration.ZERO);
        service.issue(PHONE, PHONE_HASH);

        service.verify(PHONE_HASH, sender.sentCode());
    }

    @Test
    void should_invalidate_code_after_five_failures() {
        SmsCodeService service = service(Duration.ofMinutes(5), Duration.ZERO);
        service.issue(PHONE, PHONE_HASH);

        for (int i = 0; i < 4; i++) {
            IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                    () -> service.verify(PHONE_HASH, "000000"));
            assertTrue(error.getMessage().contains("验证码错误"));
        }
        IllegalArgumentException last = assertThrows(IllegalArgumentException.class,
                () -> service.verify(PHONE_HASH, "000000"));
        assertTrue(last.getMessage().contains("作废"));
        assertEquals(5, repository.latest().getFailCount());
        assertNotNull(repository.latest().getUsedAt());
    }

    @Test
    void should_reject_expired_code() {
        SmsCodeService service = service(Duration.ofMinutes(5), Duration.ZERO);
        service.issue(PHONE, PHONE_HASH);
        SmsVerificationCode expired = repository.latest().toBuilder()
                .expiresAt(NOW.minusSeconds(1))
                .build();
        repository.save(expired);

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> service.verify(PHONE_HASH, sender.sentCode()));
        assertTrue(error.getMessage().contains("过期"));
    }

    @Test
    void should_reject_code_that_does_not_exist() {
        SmsCodeService service = service(Duration.ofMinutes(5), Duration.ZERO);

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> service.verify(PHONE_HASH, "123456"));
        assertTrue(error.getMessage().contains("不存在"));
    }

    @Test
    void should_reject_used_code() {
        SmsCodeService service = service(Duration.ofMinutes(5), Duration.ZERO);
        service.issue(PHONE, PHONE_HASH);
        service.verify(PHONE_HASH, sender.sentCode());

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> service.verify(PHONE_HASH, sender.sentCode()));
        assertTrue(error.getMessage().contains("已使用"));
    }

    /**
     * 记录发送内容的短信通道桩。
     */
    static class CapturingSmsSender implements SmsSender {
        private String sentCode;
        private int sendCount;

        @Override
        public String send(String phone, String code) {
            this.sentCode = code;
            this.sendCount++;
            return code;
        }

        String sentCode() {
            return sentCode;
        }
    }

    /**
     * 明文摘要桩：便于断言。
     */
    static class PlainHashCrypto implements PhoneCrypto {
        @Override
        public String hash(String plaintext) {
            return plaintext;
        }

        @Override
        public String encrypt(String plaintext) {
            return plaintext;
        }

        @Override
        public String decrypt(String ciphertext) {
            return ciphertext;
        }
    }
}
