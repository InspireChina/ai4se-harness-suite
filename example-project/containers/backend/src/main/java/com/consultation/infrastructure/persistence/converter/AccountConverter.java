package com.consultation.infrastructure.persistence.converter;

import com.consultation.domain.aggregate.Account;
import com.consultation.domain.vo.AccountRole;
import com.consultation.domain.vo.AccountStatus;
import com.consultation.infrastructure.persistence.po.AccountPO;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Component
@RequiredArgsConstructor
public class AccountConverter {

    private final ObjectMapper objectMapper;

    public Account toDomain(AccountPO po) {
        if (po == null) {
            return null;
        }
        Instant phoneVerifiedAt = TimeConverter.toInstant(po.getPhoneVerifiedAt());
        return Account.builder()
                .id(po.getId())
                .phoneHash(po.getPhoneHash())
                .phoneCipher(po.getPhoneCipher())
                .roles(toRoles(po.getRolesJson()))
                .status(po.getStatus() == null ? AccountStatus.ACTIVE : AccountStatus.valueOf(po.getStatus()))
                .phoneVerifiedAt(phoneVerifiedAt)
                .lastLoginAt(TimeConverter.toInstant(po.getLastLoginAt()))
                .disabledReason(po.getDisabledReason())
                .tokenVersion(po.getTokenVersion() == null ? 0 : po.getTokenVersion())
                .passwordHash(po.getPasswordHash())
                .createdAt(TimeConverter.toInstant(po.getCreatedAt()))
                .updatedAt(TimeConverter.toInstant(po.getUpdatedAt()))
                .build();
    }

    public AccountPO toPO(Account account) {
        if (account == null) {
            return null;
        }
        AccountPO po = new AccountPO();
        po.setId(account.getId());
        po.setPhoneHash(account.getPhoneHash());
        po.setPhoneCipher(account.getPhoneCipher());
        po.setRolesJson(toRolesJson(account.getRoles()));
        po.setStatus(account.getStatus().name());
        po.setPhoneVerifiedAt(TimeConverter.toLocalDateTime(account.getPhoneVerifiedAt()));
        po.setLastLoginAt(TimeConverter.toLocalDateTime(account.getLastLoginAt()));
        po.setDisabledReason(account.getDisabledReason());
        po.setTokenVersion(account.getTokenVersion());
        po.setPasswordHash(account.getPasswordHash());
        po.setCreatedAt(TimeConverter.toLocalDateTime(account.getCreatedAt()));
        po.setUpdatedAt(TimeConverter.toLocalDateTime(account.getUpdatedAt()));
        return po;
    }

    private Set<AccountRole> toRoles(String rolesJson) {
        Set<AccountRole> roles = new LinkedHashSet<>();
        if (rolesJson == null || rolesJson.isBlank()) {
            return roles;
        }
        try {
            List<String> names = objectMapper.readValue(rolesJson, new TypeReference<List<String>>() {
            });
            for (String name : names) {
                roles.add(AccountRole.valueOf(name));
            }
        } catch (Exception e) {
            throw new IllegalStateException("账号角色数据损坏：" + rolesJson);
        }
        return roles;
    }

    private String toRolesJson(Set<AccountRole> roles) {
        List<String> names = roles == null ? List.of()
                : roles.stream().map(Enum::name).sorted().toList();
        try {
            return objectMapper.writeValueAsString(names);
        } catch (Exception e) {
            throw new IllegalStateException("账号角色序列化失败");
        }
    }
}
