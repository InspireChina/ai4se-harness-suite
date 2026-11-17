package com.consultation.domain.aggregate;

import lombok.Builder;
import lombok.Getter;

import java.time.Instant;

/**
 * 用户资料：昵称、头像、邮箱、城市、语言。
 */
@Getter
@Builder(toBuilder = true)
public class UserProfile {

    public static final int NICKNAME_MIN = 2;
    public static final int NICKNAME_MAX = 30;
    public static final int EMAIL_MAX = 254;
    public static final int CITY_CODE_MAX = 20;
    public static final int LOCALE_MAX = 16;
    public static final String DEFAULT_LOCALE = "zh-CN";

    private final String accountId;
    private final String nickname;
    private final String avatarUrl;
    private final String email;
    private final String cityCode;
    private final String locale;
    private final Instant updatedAt;

    public static UserProfile create(String accountId, String nickname, String locale, Instant now) {
        return UserProfile.builder()
                .accountId(accountId)
                .nickname(validateNickname(nickname))
                .locale(validateLocale(locale))
                .updatedAt(now)
                .build();
    }

    /**
     * 更新本人资料（R-UPDATE-001：仅昵称 / 头像 / 邮箱 / 城市 / 语言可改）。
     *
     * <p>PUT 语义：可选字段传空表示清空；昵称为空表示保持原值。</p>
     */
    public UserProfile update(String nickname, String avatarUrl, String email,
                              String cityCode, String locale, Instant now) {
        return toBuilder()
                .nickname(nickname == null || nickname.isBlank() ? this.nickname : validateNickname(nickname))
                .avatarUrl(trimToNull(avatarUrl))
                .email(email == null || email.isBlank() ? null : validateEmail(email))
                .cityCode(cityCode == null || cityCode.isBlank() ? null : validateCityCode(cityCode))
                .locale(locale == null || locale.isBlank() ? this.locale : validateLocale(locale))
                .updatedAt(now)
                .build();
    }
    private static String validateNickname(String nickname) {
        if (nickname == null || nickname.isBlank()) {
            throw new IllegalArgumentException("昵称不能为空");
        }
        String trimmed = nickname.trim();
        if (trimmed.length() < NICKNAME_MIN || trimmed.length() > NICKNAME_MAX) {
            throw new IllegalArgumentException("昵称长度需为 2-30 个字符");
        }
        return trimmed;
    }

    private static String validateEmail(String email) {
        String trimmed = email.trim();
        if (trimmed.length() > EMAIL_MAX) {
            throw new IllegalArgumentException("邮箱长度不能超过 254 个字符");
        }
        if (!trimmed.matches("^[\\w.%+-]+@[\\w.-]+\\.[A-Za-z]{2,}$")) {
            throw new IllegalArgumentException("邮箱格式不正确");
        }
        return trimmed;
    }

    private static String validateLocale(String locale) {
        String trimmed = locale.trim();
        if (trimmed.length() > LOCALE_MAX) {
            throw new IllegalArgumentException("语言标识长度不能超过 16 个字符");
        }
        return trimmed;
    }

    private static String validateCityCode(String cityCode) {
        String trimmed = cityCode.trim();
        if (trimmed.length() > CITY_CODE_MAX) {
            throw new IllegalArgumentException("城市编码长度不能超过 20 个字符");
        }
        return trimmed;
    }

    private static String trimToNull(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }
}
