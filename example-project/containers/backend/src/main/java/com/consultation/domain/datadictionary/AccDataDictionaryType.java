package com.consultation.domain.datadictionary;

import com.consultation.domain.vo.AccountRole;
import com.consultation.domain.vo.AccountStatus;
import com.consultation.domain.vo.AgreementType;

/**
 * ACC 账号域数据字典类型。
 */
public enum AccDataDictionaryType implements DataDictionaryType {

    ACCOUNT_STATUS(AccountStatus.class, "账号状态"),
    ACCOUNT_ROLE(AccountRole.class, "账号角色"),
    AGREEMENT_TYPE(AgreementType.class, "协议类型");

    private final Class<? extends Description> clazz;
    private final String description;

    AccDataDictionaryType(Class<? extends Description> clazz, String description) {
        this.clazz = clazz;
        this.description = description;
    }

    @Override
    public Class<? extends Description> getClazz() {
        return clazz;
    }

    @Override
    public String getDescription() {
        return description;
    }
}
