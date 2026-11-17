package com.consultation.infrastructure.repositoryimpl;

import com.consultation.domain.aggregate.UserProfile;
import com.consultation.domain.repository.UserProfileRepository;
import com.consultation.infrastructure.persistence.converter.UserProfileConverter;
import com.consultation.infrastructure.persistence.mapper.UserProfileMapper;
import com.consultation.infrastructure.persistence.po.UserProfilePO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class UserProfileRepositoryImpl implements UserProfileRepository {

    private final UserProfileMapper mapper;
    private final UserProfileConverter converter;

    @Override
    public Optional<UserProfile> findByAccountId(String accountId) {
        return Optional.ofNullable(converter.toDomain(mapper.selectById(accountId)));
    }

    @Override
    public UserProfile save(UserProfile profile) {
        UserProfilePO po = converter.toPO(profile);
        if (mapper.selectById(po.getAccountId()) == null) {
            mapper.insert(po);
        } else {
            mapper.updateById(po);
        }
        return profile;
    }
}
