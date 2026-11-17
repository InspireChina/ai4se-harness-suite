package com.consultation.domain.vo;

/**
 * 手机号值对象：规范化（去空格与横线）并校验格式。
 */
public final class PhoneNumber {

    private static final String PATTERN = "^1[3-9]\\d{9}$";

    private final String value;

    private PhoneNumber(String value) {
        this.value = value;
    }

    public static PhoneNumber of(String raw) {
        if (raw == null) {
            throw new IllegalArgumentException("手机号不能为空");
        }
        String normalized = raw.trim().replaceAll("[\\s\\-()]", "");
        if (!normalized.matches(PATTERN)) {
            throw new IllegalArgumentException("手机号格式不正确");
        }
        return new PhoneNumber(normalized);
    }

    public String value() {
        return value;
    }

    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return value;
    }
}
