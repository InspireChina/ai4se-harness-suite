package com.consultation.infrastructure.config;

import com.consultation.domain.businessrule.BusinessRuleConfig;
import com.consultation.domain.businessrule.IBusinessRule;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

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
            if (!projected.isEmpty()) {
                detail.put("config", projected);
            }
            ruleCache.put(rule.getRuleName(), detail);
        }
    }

    public List<Map<String, Object>> getAllRules() {
        return new ArrayList<>(ruleCache.values());
    }

    private Map<String, Object> projectConfig() {
        return objectMapper.convertValue(config, new TypeReference<Map<String, Object>>() {
        });
    }
}
