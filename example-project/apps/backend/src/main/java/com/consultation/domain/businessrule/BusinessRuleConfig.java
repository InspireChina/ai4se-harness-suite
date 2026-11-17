package com.consultation.domain.businessrule;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Data
@Component
@ConfigurationProperties
public class BusinessRuleConfig {

    private Map<String, Object> appointment = new HashMap<>();

    private AuthConfig auth = new AuthConfig();

    @Data
    public static class AuthConfig {

        private PasswordConfig password = new PasswordConfig();

        private TokenConfig token = new TokenConfig();

        /**
         * 免鉴权端点列表。YAML 里写成序列，若这里声明为 Map&lt;String, Object&gt;，
         * 会被 Spring Boot 的 binder 绑成以 0/1/2… 为键的 Map，序列化出错误结构。
         */
        private List<String> publicEndpoints = new ArrayList<>(List.of(
                "/api/v1/auth/**",
                "/api/v1/home/**",
                "/api/v1/consultants/**",
                "/api/v1/data-dictionaries/**",
                "/api/v1/business-rules/**"));
    }

    @Data
    public static class PasswordConfig {

        private int minLength = 8;

        private String algorithm = "BCrypt";
    }

    @Data
    public static class TokenConfig {

        private long expirationMs = 86400000L;

        private String algorithm = "HMAC-SHA256";
    }
}
