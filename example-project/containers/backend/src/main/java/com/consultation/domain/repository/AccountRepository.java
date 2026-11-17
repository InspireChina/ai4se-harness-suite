package com.consultation.domain.repository;

import com.consultation.domain.aggregate.Account;

import java.util.Optional;

public interface AccountRepository {

    Optional<Account> findById(String id);

    Optional<Account> findByPhoneHash(String phoneHash);

    /** 新增或更新（按 id 判定）。 */
    Account save(Account account);
}
