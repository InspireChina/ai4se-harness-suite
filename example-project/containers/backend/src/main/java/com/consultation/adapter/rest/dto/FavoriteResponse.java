package com.consultation.adapter.rest.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;

@Data
@Builder
public class FavoriteResponse {

    private String id;
    private String consultantId;
    private Instant createdAt;
}
