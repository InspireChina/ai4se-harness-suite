package com.consultation.domain.repository;

import com.consultation.domain.aggregate.AgreementConsent;
import com.consultation.domain.vo.AgreementType;

import java.util.List;
import java.util.Optional;

public interface AgreementConsentRepository {

    List<AgreementConsent> findByAccountId(String accountId);

    Optional<AgreementConsent> findByAccountIdAndTypeAndVersion(String accountId, AgreementType type, String version);

    AgreementConsent save(AgreementConsent consent);
}
