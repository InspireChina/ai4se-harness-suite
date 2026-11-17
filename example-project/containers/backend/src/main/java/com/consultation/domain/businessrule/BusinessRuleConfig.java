package com.consultation.domain.businessrule;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 业务规则配置空壳。后续按 feature 扩展字段，并由 YAML 绑定。
 */
@Data
@Component
@ConfigurationProperties(prefix = "business-rules")
public class BusinessRuleConfig {

    private Map<String, Object> rules = new HashMap<>();

    private List<String> publicEndpoints = new ArrayList<>(List.of(
            "/api/v1/health"
    ));
}
