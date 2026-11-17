package com.consultation.infrastructure.persistence.converter;

import com.consultation.domain.aggregate.SmsVerificationCode;
import com.consultation.infrastructure.persistence.po.SmsVerificationCodePO;
import org.springframework.stereotype.Component;

@Component
public class SmsVerificationCodeConverter {

    public SmsVerificationCode toDomain(SmsVerificationCodePO po) {
        if (po == null) {
            return null;
        }
        return SmsVerificationCode.builder()
                .id(po.getId())
                .phoneHash(po.getPhoneHash())
                .codeHash(po.getCodeHash())
                .expiresAt(TimeConverter.toInstant(po.getExpiresAt()))
                .failCount(po.getFailCount() == null ? 0 : po.getFailCount())
                .usedAt(TimeConverter.toInstant(po.getUsedAt()))
                .createdAt(TimeConverter.toInstant(po.getCreatedAt()))
                .build();
    }

    public SmsVerificationCodePO toPO(SmsVerificationCode code) {
        if (code == null) {
            return null;
        }
        SmsVerificationCodePO po = new SmsVerificationCodePO();
        po.setId(code.getId());
        po.setPhoneHash(code.getPhoneHash());
        po.setCodeHash(code.getCodeHash());
        po.setExpiresAt(TimeConverter.toLocalDateTime(code.getExpiresAt()));
        po.setFailCount(code.getFailCount());
        po.setUsedAt(TimeConverter.toLocalDateTime(code.getUsedAt()));
        po.setCreatedAt(TimeConverter.toLocalDateTime(code.getCreatedAt()));
        return po;
    }
}
