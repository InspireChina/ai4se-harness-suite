package com.consultation.adapter.rest;

import com.consultation.adapter.rest.dto.AdminLoginRequest;
import com.consultation.adapter.rest.dto.AuthLoginResponse;
import com.consultation.adapter.rest.dto.SendSmsCodeRequest;
import com.consultation.adapter.rest.dto.SmsLoginRequest;
import com.consultation.application.service.AuthAppService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 鉴权入口：验证码发送 / 验证码登录注册 / 管理员登录。
 */
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthAppService authAppService;

    @PostMapping("/sms/send")
    public ResponseEntity<Void> sendSmsCode(@Valid @RequestBody SendSmsCodeRequest request) {
        authAppService.sendSmsCode(request.getPhone());
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/sms/login")
    public ResponseEntity<AuthLoginResponse> smsLogin(@Valid @RequestBody SmsLoginRequest request) {
        return ResponseEntity.ok(authAppService.loginOrRegister(
                request.getPhone(), request.getCode(), request.getNickname()));
    }

    @PostMapping("/admin/login")
    public ResponseEntity<AuthLoginResponse> adminLogin(@Valid @RequestBody AdminLoginRequest request) {
        return ResponseEntity.ok(authAppService.adminLogin(request.getPhone(), request.getPassword()));
    }
}
