package com.consultation.infrastructure.security;

import com.consultation.domain.service.TokenIssuer;
import com.consultation.domain.vo.AccountRole;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.List;
import java.util.Set;

/**
 * JWT 签发与校验（HMAC-SHA256）。
 *
 * <p>Claims：{@code sub}=账号 ID、{@code roles}=角色数组、{@code tokenVersion}=会话版本。</p>
 */
@Component
public class JwtTokenProvider implements TokenIssuer {

    public static final String CLAIM_ROLES = "roles";
    public static final String CLAIM_TOKEN_VERSION = "tokenVersion";

    private final SecretKey key;
    private final long expiration;

    public JwtTokenProvider(@Value("${jwt.secret}") String secret, @Value("${jwt.expiration}") long exp) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expiration = exp;
    }

    @Override
    public String issue(String accountId, Set<AccountRole> roles, int tokenVersion) {
        Date now = new Date();
        List<String> roleNames = roles == null ? List.of()
                : roles.stream().map(Enum::name).sorted().toList();
        return Jwts.builder()
                .subject(accountId)
                .claim(CLAIM_ROLES, roleNames)
                .claim(CLAIM_TOKEN_VERSION, tokenVersion)
                .issuedAt(now)
                .expiration(new Date(now.getTime() + expiration))
                .signWith(key)
                .compact();
    }

    public Claims parse(String token) {
        return Jwts.parser().verifyWith(key).build().parseSignedClaims(token).getPayload();
    }

    public boolean validate(String token) {
        try {
            parse(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
