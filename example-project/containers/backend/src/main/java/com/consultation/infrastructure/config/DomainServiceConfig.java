package com.consultation.infrastructure.config;

import com.consultation.domain.repository.SmsVerificationCodeRepository;
import com.consultation.domain.service.PhoneCrypto;
import com.consultation.domain.service.SmsCodeService;
import com.consultation.domain.service.SmsSender;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Clock;
import java.time.Duration;

/**
 * 领域服务的 Bean 注册（领域层保持纯 Java，不依赖 Spring）。
 */
@Configuration
public class DomainServiceConfig {

    @Bean
    public SmsCodeService smsCodeService(SmsVerificationCodeRepository repository,
                                         SmsSender smsSender,
                                         PhoneCrypto phoneCrypto,
                                         @Value("${sms.code.ttl-seconds:300}") long ttlSeconds,
                                         @Value("${sms.code.resend-interval-seconds:60}") long resendIntervalSeconds,
                                         @Value("${sms.code.max-failures:5}") int maxFailures) {
        return new SmsCodeService(repository, smsSender, phoneCrypto,
                Duration.ofSeconds(ttlSeconds), Duration.ofSeconds(resendIntervalSeconds), maxFailures,
                Clock.systemUTC());
    }
}
