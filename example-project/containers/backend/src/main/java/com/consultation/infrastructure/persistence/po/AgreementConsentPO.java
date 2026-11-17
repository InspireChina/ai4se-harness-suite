package com.consultation.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("agreement_consent")
public class AgreementConsentPO {

    @TableId(type = IdType.INPUT)
    private String id;
    private String accountId;
    private String agreementType;
    private String agreementVersion;
    private LocalDateTime consentedAt;
    private String sourceIp;
}
