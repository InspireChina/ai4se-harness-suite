package com.consultation.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("sms_verification_code")
public class SmsVerificationCodePO {

    @TableId(type = IdType.INPUT)
    private String id;
    private String phoneHash;
    private String codeHash;
    private LocalDateTime expiresAt;
    private Integer failCount;
    private LocalDateTime usedAt;
    private LocalDateTime createdAt;
}
