package com.consultation.domain.aggregate;

import com.consultation.domain.vo.AccountRole;
import com.consultation.domain.vo.AccountStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.Instant;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * 账号聚合根：角色集合、状态机、tokenVersion、登录校验。
 *
 * <p>不可变对象，状态流转返回新实例（{@code toBuilder}）。</p>
 */
@Getter
@Builder(toBuilder = true)
public class Account {

    private final String id;
    /** 手机号摘要，唯一登录标识。 */
    private final String phoneHash;
    /** 手机号密文，仅本人可解密查看。 */
    private final String phoneCipher;
    private final Set<AccountRole> roles;
    private final AccountStatus status;
    private final Instant phoneVerifiedAt;
    private final Instant lastLoginAt;
    private final String disabledReason;
    /** 抬升后旧 JWT 立即失效。 */
    private final int tokenVersion;
    /** 仅 ADMIN 账号使用。 */
    private final String passwordHash;
    private final Instant createdAt;
    private final Instant updatedAt;

    /**
     * 手机号验证码注册（默认 USER 角色）。已有手机号不重复建号，由 AppService 判定。
     *
     * <p>注册成功即完成一次登录，因此同时记录最近登录时间。</p>
     */
    public static Account registerByPhone(String id, String phoneHash, String phoneCipher, Instant now) {
        Set<AccountRole> roles = new LinkedHashSet<>();
        roles.add(AccountRole.USER);
        return Account.builder()
                .id(id)
                .phoneHash(phoneHash)
                .phoneCipher(phoneCipher)
                .roles(roles)
                .status(AccountStatus.ACTIVE)
                .phoneVerifiedAt(now)
                .lastLoginAt(now)
                .tokenVersion(0)
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    /**
     * 平台分配的管理员账号（R-COMMON-001：不开放自助注册）。
     */
    public static Account createAdmin(String id, String phoneHash, String phoneCipher,
                                      String passwordHash, Instant now) {
        Set<AccountRole> roles = new LinkedHashSet<>();
        roles.add(AccountRole.ADMIN);
        return Account.builder()
                .id(id)
                .phoneHash(phoneHash)
                .phoneCipher(phoneCipher)
                .roles(roles)
                .status(AccountStatus.ACTIVE)
                .phoneVerifiedAt(now)
                .tokenVersion(0)
                .passwordHash(passwordHash)
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    /**
     * 授予咨询师角色（幂等），供入驻审核通过后调用（R-UPDATE-002）。
     */
    public Account grantConsultantRole(Instant now) {
        if (roles.contains(AccountRole.CONSULTANT)) {
            return this;
        }
        Set<AccountRole> next = new LinkedHashSet<>(roles);
        next.add(AccountRole.CONSULTANT);
        return toBuilder().roles(next).updatedAt(now).build();
    }

    /**
     * 禁用账号：置 DISABLED、记录原因并抬升 tokenVersion 使既有会话失效。重复禁用幂等。
     */
    public Account disable(String reason, Instant now) {
        if (status == AccountStatus.DISABLED) {
            return this;
        }
        return toBuilder()
                .status(AccountStatus.DISABLED)
                .disabledReason(reason)
                .tokenVersion(tokenVersion + 1)
                .updatedAt(now)
                .build();
    }

    /**
     * 启用账号：回 ACTIVE 并再次抬升 tokenVersion。重复启用幂等。
     */
    public Account enable(Instant now) {
        if (status == AccountStatus.ACTIVE) {
            return this;
        }
        return toBuilder()
                .status(AccountStatus.ACTIVE)
                .disabledReason(null)
                .tokenVersion(tokenVersion + 1)
                .updatedAt(now)
                .build();
    }

    public Account touchLogin(Instant now) {
        return toBuilder().lastLoginAt(now).updatedAt(now).build();
    }

    public Account verifyPhone(Instant now) {
        return toBuilder().phoneVerifiedAt(now).updatedAt(now).build();
    }

    /**
     * 账号不可用时拒绝（EX-002 / AC-005）。
     */
    public void assertUsable() {
        if (status == AccountStatus.DISABLED) {
            throw new IllegalStateException(disabledReason == null || disabledReason.isBlank()
                    ? "账号不可用：已被禁用"
                    : "账号不可用：" + disabledReason);
        }
    }

    public boolean hasRole(AccountRole role) {
        return roles != null && roles.contains(role);
    }

    public boolean isDisabled() {
        return status == AccountStatus.DISABLED;
    }
}
