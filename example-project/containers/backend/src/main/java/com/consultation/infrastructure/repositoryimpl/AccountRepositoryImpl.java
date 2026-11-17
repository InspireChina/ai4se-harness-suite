package com.consultation.infrastructure.repositoryimpl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.consultation.domain.aggregate.Account;
import com.consultation.domain.repository.AccountRepository;
import com.consultation.infrastructure.persistence.converter.AccountConverter;
import com.consultation.infrastructure.persistence.mapper.AccountMapper;
import com.consultation.infrastructure.persistence.po.AccountPO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class AccountRepositoryImpl implements AccountRepository {

    private final AccountMapper mapper;
    private final AccountConverter converter;

    @Override
    public Optional<Account> findById(String id) {
        return Optional.ofNullable(converter.toDomain(mapper.selectById(id)));
    }

    @Override
    public Optional<Account> findByPhoneHash(String phoneHash) {
        AccountPO po = mapper.selectOne(new LambdaQueryWrapper<AccountPO>()
                .eq(AccountPO::getPhoneHash, phoneHash)
                .last("LIMIT 1"));
        return Optional.ofNullable(converter.toDomain(po));
    }

    @Override
    public Account save(Account account) {
        AccountPO po = converter.toPO(account);
        if (mapper.selectById(po.getId()) == null) {
            mapper.insert(po);
        } else {
            mapper.updateById(po);
        }
        return account;
    }
}
