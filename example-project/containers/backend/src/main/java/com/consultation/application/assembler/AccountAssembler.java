package com.consultation.application.assembler;

import com.consultation.adapter.rest.dto.AccountResponse;
import com.consultation.domain.aggregate.Account;
import com.consultation.domain.service.PhoneCrypto;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.Comparator;
import java.util.List;

@Component
@RequiredArgsConstructor
public class AccountAssembler {

    private final PhoneCrypto phoneCrypto;

    /**
     * 本人视角：手机号明文。
     */
    public AccountResponse toSelfResponse(Account account) {
        return toResponse(account, true);
    }

    /**
     * 非本人视角：手机号脱敏（R-QUERY-002）。
     */
    public AccountResponse toMaskedResponse(Account account) {
        return toResponse(account, false);
    }

    private AccountResponse toResponse(Account account, boolean revealPhone) {
        if (account == null) {
            return null;
        }
        return AccountResponse.builder()
                .id(account.getId())
                .roles(account.getRoles() == null ? List.of()
                        : account.getRoles().stream()
                        .map(Enum::name)
                        .sorted(Comparator.naturalOrder())
                        .toList())
                .status(account.getStatus() == null ? null : account.getStatus().name())
                .phone(resolvePhone(account, revealPhone))
                .phoneVerifiedAt(account.getPhoneVerifiedAt())
                .lastLoginAt(account.getLastLoginAt())
                .disabledReason(account.getDisabledReason())
                .createdAt(account.getCreatedAt())
                .updatedAt(account.getUpdatedAt())
                .build();
    }

    private String resolvePhone(Account account, boolean revealPhone) {
        if (account.getPhoneCipher() == null || account.getPhoneCipher().isBlank()) {
            return null;
        }
        String phone;
        try {
            phone = phoneCrypto.decrypt(account.getPhoneCipher());
        } catch (RuntimeException e) {
            return null;
        }
        return revealPhone ? phone : maskPhone(phone);
    }

    static String maskPhone(String phone) {
        if (phone == null || phone.length() < 7) {
            return "***";
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }
}
