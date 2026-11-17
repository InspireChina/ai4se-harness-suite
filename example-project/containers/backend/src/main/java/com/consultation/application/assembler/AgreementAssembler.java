package com.consultation.application.assembler;

import com.consultation.adapter.rest.dto.AgreementConsentResponse;
import com.consultation.domain.aggregate.AgreementConsent;
import org.springframework.stereotype.Component;

@Component
public class AgreementAssembler {

    public AgreementConsentResponse toResponse(AgreementConsent consent) {
        if (consent == null) {
            return null;
        }
        return AgreementConsentResponse.builder()
                .id(consent.getId())
                .agreementType(consent.getAgreementType().getCode())
                .agreementVersion(consent.getAgreementVersion())
                .consentedAt(consent.getConsentedAt())
                .sourceIp(consent.getSourceIp())
                .build();
    }
}
