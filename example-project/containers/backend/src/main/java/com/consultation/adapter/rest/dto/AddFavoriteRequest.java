package com.consultation.adapter.rest.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AddFavoriteRequest {

    @NotBlank(message = "咨询师ID不能为空")
    private String consultantId;
}
