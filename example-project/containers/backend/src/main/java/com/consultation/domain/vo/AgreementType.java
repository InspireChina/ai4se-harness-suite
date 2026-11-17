package com.consultation.domain.vo;

import com.consultation.domain.datadictionary.Description;

/**
 * 协议类型。领域枚举名大写，对外 API 码小写（service / privacy）。
 */
public enum AgreementType implements Description {

    SERVICE("service", "服务协议"),
    PRIVACY("privacy", "隐私政策");

    private final String code;
    private final String description;

    AgreementType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    @Override
    public String getCode() {
        return code;
    }

    @Override
    public String getDescription() {
        return description;
    }

    public static AgreementType fromCode(String code) {
        if (code != null) {
            for (AgreementType type : values()) {
                if (type.code.equalsIgnoreCase(code.trim()) || type.name().equalsIgnoreCase(code.trim())) {
                    return type;
                }
            }
        }
        throw new IllegalArgumentException("协议类型不正确");
    }
}
