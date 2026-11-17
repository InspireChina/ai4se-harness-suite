package com.consultation.infrastructure.persistence.converter;

import com.consultation.domain.aggregate.AgreementConsent;
import com.consultation.domain.vo.AgreementType;
import com.consultation.infrastructure.persistence.po.AgreementConsentPO;
import org.springframework.stereotype.Component;

@Component
public class AgreementConsentConverter {

    public AgreementConsent toDomain(AgreementConsentPO po) {
        if (po == null) {
            return null;
        }
        return AgreementConsent.builder()
                .id(po.getId())
                .accountId(po.getAccountId())
                .agreementType(AgreementType.valueOf(po.getAgreementType()))
                .agreementVersion(po.getAgreementVersion())
                .consentedAt(TimeConverter.toInstant(po.getConsentedAt()))
                .sourceIp(po.getSourceIp())
                .build();
    }

    public AgreementConsentPO toPO(AgreementConsent consent) {
        if (consent == null) {
            return null;
        }
        AgreementConsentPO po = new AgreementConsentPO();
        po.setId(consent.getId());
        po.setAccountId(consent.getAccountId());
        po.setAgreementType(consent.getAgreementType().name());
        po.setAgreementVersion(consent.getAgreementVersion());
        po.setConsentedAt(TimeConverter.toLocalDateTime(consent.getConsentedAt()));
        po.setSourceIp(consent.getSourceIp());
        return po;
    }
}
