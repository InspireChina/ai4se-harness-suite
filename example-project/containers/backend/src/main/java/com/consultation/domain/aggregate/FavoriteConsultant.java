package com.consultation.domain.aggregate;

import lombok.Builder;
import lombok.Getter;

import java.time.Instant;

/**
 * 收藏的咨询师。同一账号与咨询师只能有一条（R-CREATE-004）。
 */
@Getter
@Builder
public class FavoriteConsultant {

    private final String id;
    private final String accountId;
    private final String consultantId;
    private final Instant createdAt;
}
