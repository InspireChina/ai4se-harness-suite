package com.consultation.adapter.rest.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;

@Data
@Builder
public class ProfileResponse {

    private String accountId;
    private String nickname;
    private String avatarUrl;
    private String email;
    private String cityCode;
    private String locale;
    private Instant updatedAt;
}
