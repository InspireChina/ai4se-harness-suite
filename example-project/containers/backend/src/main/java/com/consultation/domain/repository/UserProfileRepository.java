package com.consultation.domain.repository;

import com.consultation.domain.aggregate.UserProfile;

import java.util.Optional;

public interface UserProfileRepository {

    Optional<UserProfile> findByAccountId(String accountId);

    UserProfile save(UserProfile profile);
}
