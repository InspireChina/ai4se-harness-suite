package com.consultation.adapter.rest.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class DisableAccountRequest {

    @NotBlank(message = "禁用原因不能为空")
    @Size(max = 200, message = "禁用原因长度不能超过 200 个字符")
    private String reason;
}
