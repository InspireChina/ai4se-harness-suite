package com.consultation.application.service;

import com.consultation.adapter.rest.dto.MeResponse;
import com.consultation.adapter.rest.dto.ProfileResponse;
import com.consultation.application.assembler.AccountAssembler;
import com.consultation.application.assembler.ProfileAssembler;
import com.consultation.domain.aggregate.Account;
import com.consultation.domain.aggregate.UserProfile;
import com.consultation.domain.repository.AccountRepository;
import com.consultation.domain.repository.UserProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

/**
 * 本人资料用例（R-UPDATE-001：仅本人可改）。
 */
@Service
@RequiredArgsConstructor
public class ProfileAppService {

    private final AccountRepository accountRepository;
    private final UserProfileRepository userProfileRepository;
    private final AccountAssembler accountAssembler;
    private final ProfileAssembler profileAssembler;

    public MeResponse getMe(String accountId) {
        Account account = requireAccount(accountId);
        ProfileResponse profile = profileAssembler.toResponse(
                userProfileRepository.findByAccountId(accountId).orElse(null));
        return MeResponse.builder()
                .account(accountAssembler.toSelfResponse(account))
                .profile(profile)
                .build();
    }

    @Transactional
    public ProfileResponse updateProfile(String accountId, String nickname, String avatarUrl,
                                         String email, String cityCode, String locale) {
        requireAccount(accountId);
        Instant now = Instant.now();
        UserProfile profile = userProfileRepository.findByAccountId(accountId)
                .map(existing -> existing.update(nickname, avatarUrl, email, cityCode, locale, now))
                .orElseGet(() -> UserProfile.create(accountId,
                        nickname == null || nickname.isBlank() ? "用户" : nickname,
                        locale == null || locale.isBlank() ? UserProfile.DEFAULT_LOCALE : locale,
                        now));
        userProfileRepository.save(profile);
        return profileAssembler.toResponse(profile);
    }

    private Account requireAccount(String accountId) {
        return accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("账号不存在"));
    }
}
