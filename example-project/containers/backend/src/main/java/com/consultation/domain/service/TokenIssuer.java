package com.consultation.domain.service;

import com.consultation.domain.vo.AccountRole;

import java.util.Set;

/**
 * 令牌签发端口。实现位于 infrastructure（本期为 JWT HMAC-SHA256）。
 */
public interface TokenIssuer {

    String issue(String accountId, Set<AccountRole> roles, int tokenVersion);
}
