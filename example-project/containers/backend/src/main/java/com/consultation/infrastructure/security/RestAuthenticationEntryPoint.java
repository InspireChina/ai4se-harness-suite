package com.consultation.infrastructure.security;

import com.consultation.infrastructure.config.GlobalExceptionHandler;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * 未认证（401）响应。鉴权失败不走 GlobalExceptionHandler，由 Spring Security 直接返回，
 * 但沿用统一响应体结构，便于前端统一提示。
 */
@Component
@RequiredArgsConstructor
public class RestAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private final ObjectMapper objectMapper;

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                         AuthenticationException authException) throws IOException {
        Object message = request.getAttribute(AuthErrorMessage.ATTRIBUTE);
        String errorMessage = message == null ? "未登录或登录已过期" : String.valueOf(message);
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        objectMapper.writeValue(response.getWriter(),
                new GlobalExceptionHandler.ErrorResponse("UNAUTHORIZED", errorMessage, null));
    }
}
