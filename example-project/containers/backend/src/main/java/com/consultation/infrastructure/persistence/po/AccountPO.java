package com.consultation.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("account")
public class AccountPO {

    @TableId(type = IdType.INPUT)
    private String id;
    private String phoneHash;
    private String phoneCipher;
    private String rolesJson;
    private String status;
    private LocalDateTime phoneVerifiedAt;
    private LocalDateTime lastLoginAt;
    private String disabledReason;
    private Integer tokenVersion;
    private String passwordHash;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
