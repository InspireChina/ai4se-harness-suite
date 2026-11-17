package com.consultation.infrastructure.repositoryimpl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.consultation.domain.aggregate.SmsVerificationCode;
import com.consultation.domain.repository.SmsVerificationCodeRepository;
import com.consultation.infrastructure.persistence.converter.SmsVerificationCodeConverter;
import com.consultation.infrastructure.persistence.mapper.SmsVerificationCodeMapper;
import com.consultation.infrastructure.persistence.po.SmsVerificationCodePO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class SmsVerificationCodeRepositoryImpl implements SmsVerificationCodeRepository {

    private final SmsVerificationCodeMapper mapper;
    private final SmsVerificationCodeConverter converter;

    @Override
    public Optional<SmsVerificationCode> findLatestByPhoneHash(String phoneHash) {
        SmsVerificationCodePO po = mapper.selectOne(new LambdaQueryWrapper<SmsVerificationCodePO>()
                .eq(SmsVerificationCodePO::getPhoneHash, phoneHash)
                .orderByDesc(SmsVerificationCodePO::getCreatedAt)
                .last("LIMIT 1"));
        return Optional.ofNullable(converter.toDomain(po));
    }

    @Override
    public SmsVerificationCode save(SmsVerificationCode code) {
        SmsVerificationCodePO po = converter.toPO(code);
        if (mapper.selectById(po.getId()) == null) {
            mapper.insert(po);
        } else {
            mapper.updateById(po);
        }
        return code;
    }
}
