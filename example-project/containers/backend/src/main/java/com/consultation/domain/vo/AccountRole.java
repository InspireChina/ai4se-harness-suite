package com.consultation.domain.vo;

import com.consultation.domain.datadictionary.Description;

/**
 * 账号角色。JWT authority = {@code ROLE_<name>}，与 Spring Security {@code hasRole} 对齐。
 */
public enum AccountRole implements Description {

    USER("终端用户"),
    CONSULTANT("咨询师"),
    ADMIN("管理员");

    private final String description;

    AccountRole(String description) {
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

    public String authority() {
        return "ROLE_" + name();
    }
}
