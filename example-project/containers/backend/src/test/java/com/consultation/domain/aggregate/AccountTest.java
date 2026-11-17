package com.consultation.domain.aggregate;

import com.consultation.domain.vo.AccountRole;
import com.consultation.domain.vo.AccountStatus;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AccountTest {

    private static final Instant NOW = Instant.parse("2026-11-17T10:00:00Z");

    private Account activeAccount() {
        return Account.registerByPhone("acc-1", "hash", "cipher", NOW);
    }

    @Test
    void should_register_account_with_user_role_and_active_status() {
        Account account = activeAccount();

        assertEquals(AccountStatus.ACTIVE, account.getStatus());
        assertEquals(Set.of(AccountRole.USER), account.getRoles());
        assertEquals(0, account.getTokenVersion());
        assertTrue(account.hasRole(AccountRole.USER));
    }

    @Test
    void should_disable_account_and_bump_token_version() {
        Account disabled = activeAccount().disable("违规内容", NOW);

        assertEquals(AccountStatus.DISABLED, disabled.getStatus());
        assertEquals("违规内容", disabled.getDisabledReason());
        assertEquals(1, disabled.getTokenVersion());
    }

    @Test
    void should_keep_disable_idempotent_without_bumping_token_version() {
        Account once = activeAccount().disable("违规内容", NOW);
        Account twice = once.disable("违规内容", NOW);

        assertEquals(once, twice);
        assertEquals(1, twice.getTokenVersion());
    }

    @Test
    void should_enable_account_and_bump_token_version() {
        Account disabled = activeAccount().disable("违规内容", NOW);
        Account enabled = disabled.enable(NOW);

        assertEquals(AccountStatus.ACTIVE, enabled.getStatus());
        assertEquals(null, enabled.getDisabledReason());
        assertEquals(2, enabled.getTokenVersion());
    }

    @Test
    void should_keep_enable_idempotent_when_already_active() {
        Account enabled = activeAccount().enable(NOW);

        assertEquals(AccountStatus.ACTIVE, enabled.getStatus());
        assertEquals(0, enabled.getTokenVersion());
    }

    @Test
    void should_grant_consultant_role_idempotently() {
        Account granted = activeAccount().grantConsultantRole(NOW);
        Account grantedAgain = granted.grantConsultantRole(NOW);

        assertTrue(granted.hasRole(AccountRole.CONSULTANT));
        assertTrue(granted.hasRole(AccountRole.USER));
        assertEquals(granted, grantedAgain);
    }

    @Test
    void should_reject_disabled_account_when_assert_usable() {
        Account disabled = activeAccount().disable("违规内容", NOW);

        IllegalStateException error = assertThrows(IllegalStateException.class, disabled::assertUsable);
        assertTrue(error.getMessage().contains("账号不可用"));
        assertTrue(error.getMessage().contains("违规内容"));
    }

    @Test
    void should_touch_login_time() {
        Instant later = NOW.plusSeconds(60);
        Account touched = activeAccount().touchLogin(later);

        assertEquals(later, touched.getLastLoginAt());
        assertNotEquals(activeAccount().getLastLoginAt(), touched.getLastLoginAt());
    }

    @Test
    void should_create_admin_account_without_user_role() {
        Account admin = Account.createAdmin("acc-admin", "hash", "cipher", "pwd", NOW);

        assertTrue(admin.hasRole(AccountRole.ADMIN));
        assertFalse(admin.hasRole(AccountRole.USER));
        assertEquals("pwd", admin.getPasswordHash());
    }
}
