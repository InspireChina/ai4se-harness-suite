package com.consultation.application.service;

import com.consultation.adapter.rest.dto.AgreementConsentResponse;
import com.consultation.application.assembler.AgreementAssembler;
import com.consultation.domain.aggregate.AgreementConsent;
import com.consultation.domain.repository.AgreementConsentRepository;
import com.consultation.domain.vo.AgreementType;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

/**
 * 协议同意用例（R-CREATE-003：按类型 + 版本幂等，记录时间与来源 IP）。
 */
@Service
@RequiredArgsConstructor
public class AgreementAppService {

    private final AgreementConsentRepository consentRepository;
    private final AgreementAssembler agreementAssembler;

    public List<AgreementConsentResponse> list(String accountId) {
        return consentRepository.findByAccountId(accountId).stream()
                .map(agreementAssembler::toResponse)
                .toList();
    }

    @Transactional
    public AgreementConsentResponse consent(String accountId, String agreementType, String agreementVersion,
                                            String sourceIp) {
        AgreementType type = AgreementType.fromCode(agreementType);
        if (agreementVersion == null || agreementVersion.isBlank()) {
            throw new IllegalArgumentException("协议版本不能为空");
        }
        String version = agreementVersion.trim();
        if (version.length() > 20) {
            throw new IllegalArgumentException("协议版本长度不能超过 20 个字符");
        }
        return consentRepository.findByAccountIdAndTypeAndVersion(accountId, type, version)
                .map(agreementAssembler::toResponse)
                .orElseGet(() -> {
                    AgreementConsent created = AgreementConsent.builder()
                            .id(UUID.randomUUID().toString())
                            .accountId(accountId)
                            .agreementType(type)
                            .agreementVersion(version)
                            .consentedAt(Instant.now())
                            .sourceIp(sourceIp == null || sourceIp.isBlank() ? "unknown" : sourceIp)
                            .build();
                    return agreementAssembler.toResponse(consentRepository.save(created));
                });
    }
}
