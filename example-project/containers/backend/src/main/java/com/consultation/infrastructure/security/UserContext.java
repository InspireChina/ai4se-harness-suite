package com.consultation.infrastructure.security;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

import java.util.Set;

/**
 * 当前请求的用户上下文。roles 为 Spring Security authority 集合（ROLE_USER 等）。
 */
@Data
@Builder
@AllArgsConstructor
public class UserContext {

    private String userId;
    private Set<String> roles;

    public boolean hasRole(String role) {
        if (role == null || roles == null) {
            return false;
        }
        String authority = role.startsWith("ROLE_") ? role : "ROLE_" + role;
        return roles.contains(authority);
    }
}
