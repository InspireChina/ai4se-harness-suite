package com.consultation.domain.service;

import com.consultation.domain.aggregate.SmsVerificationCode;
import com.consultation.domain.repository.SmsVerificationCodeRepository;

import java.util.Optional;

class FakeSmsVerificationCodeRepository implements SmsVerificationCodeRepository {

    private SmsVerificationCode latest;

    @Override
    public Optional<SmsVerificationCode> findLatestByPhoneHash(String phoneHash) {
        return Optional.ofNullable(latest);
    }

    @Override
    public SmsVerificationCode save(SmsVerificationCode code) {
        this.latest = code;
        return code;
    }

    SmsVerificationCode latest() {
        return latest;
    }
}
