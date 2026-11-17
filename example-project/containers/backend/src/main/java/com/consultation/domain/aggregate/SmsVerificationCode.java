package com.consultation.domain.aggregate;

import lombok.Builder;
import lombok.Getter;

import java.time.Instant;

/**
 * 短信验证码：DB 存储，无 Redis 依赖。TTL + 连续失败次数控制（R-CREATE-002）。
 */
@Getter
@Builder(toBuilder = true)
public class SmsVerificationCode {

    private final String id;
    private final String phoneHash;
    private final String codeHash;
    private final Instant expiresAt;
    private final int failCount;
    /** 非空表示已使用或已作废。 */
    private final Instant usedAt;
    private final Instant createdAt;

    public boolean isExpired(Instant now) {
        return now.isAfter(expiresAt);
    }

    public boolean isUsed() {
        return usedAt != null;
    }

    public boolean matches(String candidateHash) {
        return codeHash.equals(candidateHash);
    }

    public SmsVerificationCode recordFailure() {
        return toBuilder().failCount(failCount + 1).build();
    }

    /** 标记为已使用 / 已作废。 */
    public SmsVerificationCode invalidate(Instant now) {
        return toBuilder().usedAt(now).build();
    }
}
