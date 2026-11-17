package com.consultation.adapter.rest.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;

@Data
@Builder
public class AgreementConsentResponse {

    private String id;
    /** service / privacy */
    private String agreementType;
    private String agreementVersion;
    private Instant consentedAt;
    private String sourceIp;
}
