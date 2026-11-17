package com.consultation.domain.repository;

import com.consultation.domain.aggregate.FavoriteConsultant;

import java.util.List;
import java.util.Optional;

public interface FavoriteConsultantRepository {

    List<FavoriteConsultant> findByAccountId(String accountId);

    Optional<FavoriteConsultant> findByAccountIdAndConsultantId(String accountId, String consultantId);

    FavoriteConsultant save(FavoriteConsultant favorite);

    /** 取消收藏；记录不存在时静默成功（幂等）。 */
    void deleteByAccountIdAndConsultantId(String accountId, String consultantId);
}
