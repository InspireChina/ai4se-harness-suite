package com.consultation.infrastructure.config;

import com.consultation.domain.businessrule.BusinessRuleConfig;
import com.consultation.domain.businessrule.IBusinessRule;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.*;

@Component
@RequiredArgsConstructor
public class BusinessRuleProvider {

    private final BusinessRuleConfig config;
    private final List<IBusinessRule> ruleDefinitions;
    private final ObjectMapper objectMapper;
    private final Map<String, Map<String, Object>> ruleCache = new LinkedHashMap<>();

    @PostConstruct
    public void init() {
        Map<String, Object> projected = projectConfig();
        for (IBusinessRule rule : ruleDefinitions) {
            Map<String, Object> detail = new LinkedHashMap<>();
            detail.put("ruleName", rule.getRuleName());
            detail.put("description", rule.getDescription());

            Map<String, Object> ruleConfig = new LinkedHashMap<>();
            addIfPresent(ruleConfig, "appointment", projected.get("appointment"));
            addIfPresent(ruleConfig, "auth", projected.get("auth"));
            if (!ruleConfig.isEmpty()) detail.put("config", ruleConfig);

            ruleCache.put(rule.getRuleName(), detail);
        }
    }

    public List<Map<String, Object>> getAllRules() {
        return new ArrayList<Map<String, Object>>(ruleCache.values());
    }

    /**
     * 把强类型的配置对象投影成 Map，保持对外返回结构为 {@code List<Map<String, Object>>}。
     * JSON 形状属于基础设施关注点，故投影放在 infrastructure 层，domain 不依赖 ObjectMapper。
     */
    private Map<String, Object> projectConfig() {
        return objectMapper.convertValue(config, new TypeReference<Map<String, Object>>() {
        });
    }

    private void addIfPresent(Map<String, Object> target, String key, Object source) {
        if (source instanceof Map<?, ?> map && !map.isEmpty()) target.put(key, map);
    }
}
