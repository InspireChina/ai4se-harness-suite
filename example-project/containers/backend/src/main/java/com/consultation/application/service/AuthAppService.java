package com.consultation.application.service;

import com.consultation.adapter.rest.dto.AccountResponse;
import com.consultation.adapter.rest.dto.AuthLoginResponse;
import com.consultation.adapter.rest.dto.ProfileResponse;
import com.consultation.application.assembler.AccountAssembler;
import com.consultation.application.assembler.ProfileAssembler;
import com.consultation.domain.aggregate.Account;
import com.consultation.domain.aggregate.UserProfile;
import com.consultation.domain.repository.AccountRepository;
import com.consultation.domain.repository.UserProfileRepository;
import com.consultation.domain.service.PasswordService;
import com.consultation.domain.service.PhoneCrypto;
import com.consultation.domain.service.SmsCodeService;
import com.consultation.domain.service.TokenIssuer;
import com.consultation.domain.vo.AccountRole;
import com.consultation.domain.vo.PhoneNumber;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/**
 * 登录 / 注册用例编排。
 *
 * <p>手机号验证码登录与注册合一：已有手机号不重复建号（R-CREATE-001）。</p>
 */
@Service
@RequiredArgsConstructor
public class AuthAppService {

    private static final SecureRandom RANDOM = new SecureRandom();

    private final AccountRepository accountRepository;
    private final UserProfileRepository userProfileRepository;
    private final SmsCodeService smsCodeService;
    private final PhoneCrypto phoneCrypto;
    private final PasswordService passwordService;
    private final TokenIssuer tokenIssuer;
    private final AccountAssembler accountAssembler;
    private final ProfileAssembler profileAssembler;

    /**
     * 发送登录 / 注册验证码。不区分手机号是否存在，防枚举。
     */
    public void sendSmsCode(String phone) {
        PhoneNumber phoneNumber = PhoneNumber.of(phone);
        smsCodeService.issue(phoneNumber.value(), phoneCrypto.hash(phoneNumber.value()));
    }

    /**
     * 验证码登录或注册（默认 USER 角色）。
     */
    @Transactional
    public AuthLoginResponse loginOrRegister(String phone, String code, String nickname) {
        PhoneNumber phoneNumber = PhoneNumber.of(phone);
        String phoneHash = phoneCrypto.hash(phoneNumber.value());
        smsCodeService.verify(phoneHash, code);

        Instant now = Instant.now();
        Optional<Account> existing = accountRepository.findByPhoneHash(phoneHash);
        Account account;
        ProfileResponse profile;
        if (existing.isPresent()) {
            account = existing.get();
            account.assertUsable();
            account = account.touchLogin(now);
            accountRepository.save(account);
            profile = profileAssembler.toResponse(
                    userProfileRepository.findByAccountId(account.getId()).orElse(null));
        } else {
            account = Account.registerByPhone(
                    UUID.randomUUID().toString(), phoneHash, phoneCrypto.encrypt(phoneNumber.value()), now);
            accountRepository.save(account);
            UserProfile created = UserProfile.create(
                    account.getId(), resolveNickname(nickname), UserProfile.DEFAULT_LOCALE, now);
            userProfileRepository.save(created);
            profile = profileAssembler.toResponse(created);
        }
        return buildLoginResponse(account, profile);
    }

    /**
     * 管理员密码登录（独立鉴权，R-COMMON-001：不开放自助注册 ADMIN）。
     */
    @Transactional
    public AuthLoginResponse adminLogin(String phone, String password) {
        PhoneNumber phoneNumber = PhoneNumber.of(phone);
        String phoneHash = phoneCrypto.hash(phoneNumber.value());
        Account account = accountRepository.findByPhoneHash(phoneHash)
                .orElseThrow(() -> new IllegalArgumentException("账号或密码不正确"));
        if (!account.hasRole(AccountRole.ADMIN)) {
            throw new IllegalArgumentException("账号或密码不正确");
        }
        if (account.getPasswordHash() == null || !passwordService.matches(password, account.getPasswordHash())) {
            throw new IllegalArgumentException("账号或密码不正确");
        }
        account.assertUsable();
        account = account.touchLogin(Instant.now());
        accountRepository.save(account);

        ProfileResponse profile = profileAssembler.toResponse(
                userProfileRepository.findByAccountId(account.getId()).orElse(null));
        return buildLoginResponse(account, profile);
    }

    private AuthLoginResponse buildLoginResponse(Account account, ProfileResponse profile) {
        String token = tokenIssuer.issue(account.getId(), account.getRoles(), account.getTokenVersion());
        return AuthLoginResponse.builder()
                .token(token)
                .account(accountAssembler.toSelfResponse(account))
                .profile(profile)
                .build();
    }

    private String resolveNickname(String nickname) {
        if (nickname != null && !nickname.isBlank()) {
            return nickname.trim();
        }
        return "用户" + String.format("%04d", RANDOM.nextInt(10_000));
    }

    /** 仅供后续 feature 复用：当前账号的对外视图。 */
    public AccountResponse toSelfResponse(Account account) {
        return accountAssembler.toSelfResponse(account);
    }
}
