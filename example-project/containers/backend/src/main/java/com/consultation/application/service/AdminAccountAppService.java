package com.consultation.application.service;

import com.consultation.adapter.rest.dto.AccountResponse;
import com.consultation.application.assembler.AccountAssembler;
import com.consultation.domain.aggregate.Account;
import com.consultation.domain.repository.AccountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

/**
 * 管理端账号操作（R-UPDATE-003：禁用必须填原因并使现有会话失效）。
 */
@Service
@RequiredArgsConstructor
public class AdminAccountAppService {

    private final AccountRepository accountRepository;
    private final AccountAssembler accountAssembler;

    /**
     * 禁用账号：抬升 tokenVersion，既有 JWT 立即失效。重复禁用幂等。
     */
    @Transactional
    public AccountResponse disable(String accountId, String reason) {
        if (reason == null || reason.isBlank()) {
            throw new IllegalArgumentException("禁用原因不能为空");
        }
        String trimmed = reason.trim();
        if (trimmed.length() > 200) {
            throw new IllegalArgumentException("禁用原因长度不能超过 200 个字符");
        }
        Account account = requireAccount(accountId);
        Account disabled = account.disable(trimmed, Instant.now());
        if (disabled != account) {
            accountRepository.save(disabled);
        }
        return accountAssembler.toMaskedResponse(disabled);
    }

    /**
     * 启用账号：同样抬升 tokenVersion，旧令牌不再可用。重复启用幂等。
     */
    @Transactional
    public AccountResponse enable(String accountId) {
        Account account = requireAccount(accountId);
        Account enabled = account.enable(Instant.now());
        if (enabled != account) {
            accountRepository.save(enabled);
        }
        return accountAssembler.toMaskedResponse(enabled);
    }

    private Account requireAccount(String accountId) {
        return accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("账号不存在"));
    }
}
