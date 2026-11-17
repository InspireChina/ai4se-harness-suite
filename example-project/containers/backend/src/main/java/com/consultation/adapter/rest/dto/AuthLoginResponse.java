package com.consultation.adapter.rest.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AuthLoginResponse {

    private String token;
    private AccountResponse account;
    private ProfileResponse profile;
}
