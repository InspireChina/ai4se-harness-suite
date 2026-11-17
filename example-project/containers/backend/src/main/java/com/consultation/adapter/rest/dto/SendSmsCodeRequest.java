package com.consultation.adapter.rest.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class SendSmsCodeRequest {

    @NotBlank(message = "手机号不能为空")
    private String phone;
}
