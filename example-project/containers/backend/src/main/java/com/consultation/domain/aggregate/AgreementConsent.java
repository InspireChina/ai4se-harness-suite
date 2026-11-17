package com.consultation.domain.aggregate;

import com.consultation.domain.vo.AgreementType;
import lombok.Builder;
import lombok.Getter;

import java.time.Instant;

/**
 * 协议同意记录：不可变、不可物理删除（DATA-001）。
 */
@Getter
@Builder
public class AgreementConsent {

    private final String id;
    private final String accountId;
    private final AgreementType agreementType;
    private final String agreementVersion;
    private final Instant consentedAt;
    private final String sourceIp;
}
