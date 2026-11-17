package com.consultation.infrastructure.security;

import com.consultation.domain.aggregate.Account;
import com.consultation.domain.repository.AccountRepository;
import com.consultation.domain.vo.AccountRole;
import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * JWT 鉴权过滤器：验签 → 校验账号状态与 tokenVersion → 写入用户上下文。
 *
 * <p>账号被禁用或 tokenVersion 不一致（被禁用抬升）时不予放行，由认证入口点返回 401。</p>
 */
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider tokenProvider;
    private final AccountRepository accountRepository;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String bearer = request.getHeader("Authorization");
        if (StringUtils.hasText(bearer) && bearer.startsWith("Bearer ")) {
            authenticate(bearer.substring(7), request);
        }
        try {
            chain.doFilter(request, response);
        } finally {
            UserContextHolder.clear();
            SecurityContextHolder.clearContext();
        }
    }

    private void authenticate(String token, HttpServletRequest request) {
        if (!tokenProvider.validate(token)) {
            request.setAttribute(AuthErrorMessage.ATTRIBUTE, "登录状态无效或已过期");
            return;
        }
        Claims claims = tokenProvider.parse(token);
        String accountId = claims.getSubject();
        Integer tokenVersion = claims.get(JwtTokenProvider.CLAIM_TOKEN_VERSION, Integer.class);
        Optional<Account> found = accountId == null ? Optional.empty() : accountRepository.findById(accountId);
        if (found.isEmpty()) {
            request.setAttribute(AuthErrorMessage.ATTRIBUTE, "登录状态已失效，请重新登录");
            return;
        }
        Account account = found.get();
        if (account.isDisabled()) {
            request.setAttribute(AuthErrorMessage.ATTRIBUTE, account.getDisabledReason() == null
                    ? "账号不可用：已被禁用"
                    : "账号不可用：" + account.getDisabledReason());
            return;
        }
        if (tokenVersion == null || tokenVersion.intValue() != account.getTokenVersion()) {
            request.setAttribute(AuthErrorMessage.ATTRIBUTE, "登录状态已失效，请重新登录");
            return;
        }

        Set<String> authorities = new LinkedHashSet<>();
        for (AccountRole role : account.getRoles()) {
            authorities.add(role.authority());
        }
        UserContextHolder.set(UserContext.builder()
                .userId(account.getId())
                .roles(authorities)
                .build());
        SecurityContextHolder.getContext().setAuthentication(
                new UsernamePasswordAuthenticationToken(
                        account.getId(), null,
                        authorities.stream().map(SimpleGrantedAuthority::new).toList()
                )
        );
    }

    /** 读取令牌中的角色声明（调试用）。 */
    static List<String> rolesOf(Claims claims) {
        Object raw = claims.get(JwtTokenProvider.CLAIM_ROLES);
        if (raw instanceof List<?> list) {
            return list.stream().map(String::valueOf).toList();
        }
        return List.of();
    }
}
