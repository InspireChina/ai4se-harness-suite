package com.consultation.adapter.rest.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class MeResponse {

    private AccountResponse account;
    private ProfileResponse profile;
}
