package com.consultation.adapter.rest.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.List;

/**
 * 账号对外视图。手机号仅本人查看时明文，其余场景脱敏（R-QUERY-002）。
 */
@Data
@Builder
public class AccountResponse {

    private String id;
    private List<String> roles;
    private String status;
    private String phone;
    private Instant phoneVerifiedAt;
    private Instant lastLoginAt;
    private String disabledReason;
    private Instant createdAt;
    private Instant updatedAt;
}
