package com.consultation.infrastructure.repositoryimpl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.consultation.domain.aggregate.FavoriteConsultant;
import com.consultation.domain.repository.FavoriteConsultantRepository;
import com.consultation.infrastructure.persistence.converter.FavoriteConsultantConverter;
import com.consultation.infrastructure.persistence.mapper.FavoriteConsultantMapper;
import com.consultation.infrastructure.persistence.po.FavoriteConsultantPO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class FavoriteConsultantRepositoryImpl implements FavoriteConsultantRepository {

    private final FavoriteConsultantMapper mapper;
    private final FavoriteConsultantConverter converter;

    @Override
    public List<FavoriteConsultant> findByAccountId(String accountId) {
        return mapper.selectList(new LambdaQueryWrapper<FavoriteConsultantPO>()
                        .eq(FavoriteConsultantPO::getAccountId, accountId)
                        .orderByDesc(FavoriteConsultantPO::getCreatedAt))
                .stream().map(converter::toDomain).toList();
    }

    @Override
    public Optional<FavoriteConsultant> findByAccountIdAndConsultantId(String accountId, String consultantId) {
        FavoriteConsultantPO po = mapper.selectOne(new LambdaQueryWrapper<FavoriteConsultantPO>()
                .eq(FavoriteConsultantPO::getAccountId, accountId)
                .eq(FavoriteConsultantPO::getConsultantId, consultantId)
                .last("LIMIT 1"));
        return Optional.ofNullable(converter.toDomain(po));
    }

    @Override
    public FavoriteConsultant save(FavoriteConsultant favorite) {
        mapper.insert(converter.toPO(favorite));
        return favorite;
    }

    @Override
    public void deleteByAccountIdAndConsultantId(String accountId, String consultantId) {
        mapper.delete(new LambdaQueryWrapper<FavoriteConsultantPO>()
                .eq(FavoriteConsultantPO::getAccountId, accountId)
                .eq(FavoriteConsultantPO::getConsultantId, consultantId));
    }
}
