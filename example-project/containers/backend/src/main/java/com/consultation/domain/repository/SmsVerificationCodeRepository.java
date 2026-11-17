package com.consultation.domain.repository;

import com.consultation.domain.aggregate.SmsVerificationCode;

import java.util.Optional;

public interface SmsVerificationCodeRepository {

    /** 该手机号最近一条未失效的验证码（按创建时间倒序取第一条）。 */
    Optional<SmsVerificationCode> findLatestByPhoneHash(String phoneHash);

    SmsVerificationCode save(SmsVerificationCode code);
}
