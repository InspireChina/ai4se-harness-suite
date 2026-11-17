package com.consultation.domain.vo;

import com.consultation.domain.datadictionary.Description;

/**
 * 账号状态。对外 JSON 与库内取值统一使用大写枚举名。
 */
public enum AccountStatus implements Description {

    ACTIVE("正常"),
    DISABLED("已禁用");

    private final String description;

    AccountStatus(String description) {
        this.description = description;
    }

    @Override
    public String getCode() {
        return name();
    }

    @Override
    public String getDescription() {
        return description;
    }
}
