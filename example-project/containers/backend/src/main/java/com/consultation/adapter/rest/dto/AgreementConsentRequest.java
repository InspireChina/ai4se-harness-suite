package com.consultation.adapter.rest.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class AgreementConsentRequest {

    /** service / privacy */
    @NotBlank(message = "协议类型不能为空")
    private String agreementType;

    @NotBlank(message = "协议版本不能为空")
    @Size(max = 20, message = "协议版本长度不能超过 20 个字符")
    private String agreementVersion;
}
