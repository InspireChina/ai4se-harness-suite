package com.consultation.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("favorite_consultant")
public class FavoriteConsultantPO {

    @TableId(type = IdType.INPUT)
    private String id;
    private String accountId;
    private String consultantId;
    private LocalDateTime createdAt;
}
