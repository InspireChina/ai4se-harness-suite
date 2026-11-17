package com.consultation.infrastructure.repositoryimpl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.consultation.domain.aggregate.AgreementConsent;
import com.consultation.domain.repository.AgreementConsentRepository;
import com.consultation.domain.vo.AgreementType;
import com.consultation.infrastructure.persistence.converter.AgreementConsentConverter;
import com.consultation.infrastructure.persistence.mapper.AgreementConsentMapper;
import com.consultation.infrastructure.persistence.po.AgreementConsentPO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class AgreementConsentRepositoryImpl implements AgreementConsentRepository {

    private final AgreementConsentMapper mapper;
    private final AgreementConsentConverter converter;

    @Override
    public List<AgreementConsent> findByAccountId(String accountId) {
        return mapper.selectList(new LambdaQueryWrapper<AgreementConsentPO>()
                        .eq(AgreementConsentPO::getAccountId, accountId)
                        .orderByDesc(AgreementConsentPO::getConsentedAt))
                .stream().map(converter::toDomain).toList();
    }

    @Override
    public Optional<AgreementConsent> findByAccountIdAndTypeAndVersion(String accountId, AgreementType type,
                                                                       String version) {
        AgreementConsentPO po = mapper.selectOne(new LambdaQueryWrapper<AgreementConsentPO>()
                .eq(AgreementConsentPO::getAccountId, accountId)
                .eq(AgreementConsentPO::getAgreementType, type.name())
                .eq(AgreementConsentPO::getAgreementVersion, version)
                .last("LIMIT 1"));
        return Optional.ofNullable(converter.toDomain(po));
    }

    @Override
    public AgreementConsent save(AgreementConsent consent) {
        mapper.insert(converter.toPO(consent));
        return consent;
    }
}
