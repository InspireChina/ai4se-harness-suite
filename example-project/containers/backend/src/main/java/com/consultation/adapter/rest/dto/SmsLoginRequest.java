package com.consultation.adapter.rest.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class SmsLoginRequest {

    @NotBlank(message = "手机号不能为空")
    private String phone;

    @NotBlank(message = "验证码不能为空")
    private String code;

    /** 新号注册时的昵称，缺省由系统生成。 */
    private String nickname;
}
