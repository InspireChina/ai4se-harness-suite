package com.consultation.infrastructure.security;

public class SecurityUtils {

    private SecurityUtils() {
    }

    public static UserContext currentUser() {
        UserContext c = UserContextHolder.get();
        if (c == null) {
            throw new IllegalStateException("未登录");
        }
        return c;
    }

    public static String currentUserId() {
        return currentUser().getUserId();
    }

    /**
     * 是否具备指定角色。参数可写 "CONSULTANT" 或 "ROLE_CONSULTANT"。
     */
    public static boolean hasRole(String role) {
        UserContext c = UserContextHolder.get();
        return c != null && c.hasRole(role);
    }

    public static boolean isAdmin() {
        return hasRole("ADMIN");
    }
}
