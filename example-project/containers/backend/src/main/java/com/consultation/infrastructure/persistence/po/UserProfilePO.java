package com.consultation.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("user_profile")
public class UserProfilePO {

    @TableId(type = IdType.INPUT)
    private String accountId;
    private String nickname;
    private String avatarUrl;
    private String email;
    private String cityCode;
    private String locale;
    private LocalDateTime updatedAt;
}
