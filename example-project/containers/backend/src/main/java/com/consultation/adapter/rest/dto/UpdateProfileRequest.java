package com.consultation.adapter.rest.dto;

import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class UpdateProfileRequest {

    @Size(min = 2, max = 30, message = "昵称长度需为 2-30 个字符")
    private String nickname;

    @Size(max = 500, message = "头像地址长度不能超过 500 个字符")
    private String avatarUrl;

    @Size(max = 254, message = "邮箱长度不能超过 254 个字符")
    private String email;

    @Size(max = 20, message = "城市编码长度不能超过 20 个字符")
    private String cityCode;

    @Size(max = 16, message = "语言标识长度不能超过 16 个字符")
    private String locale;
}
