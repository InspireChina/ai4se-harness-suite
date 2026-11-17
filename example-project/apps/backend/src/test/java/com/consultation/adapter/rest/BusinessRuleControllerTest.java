package com.consultation.adapter.rest;

import com.consultation.TestBase;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;

class BusinessRuleControllerTest extends TestBase {

    @Test
    void should_list_all_business_rules() {
        given()
        .when()
            .get("/api/v1/business-rules")
        .then()
            .statusCode(200)
            .body("$", not(empty()))
            .body("$", hasSize(7));
    }

    @Test
    void should_contain_appointment_conflict_detection_rule() {
        given()
        .when()
            .get("/api/v1/business-rules")
        .then()
            .statusCode(200)
            .body("ruleName", hasItem("appointment_conflict_detection"));

        assertThat(descriptionOf("appointment_conflict_detection"), not(isEmptyOrNullString()));
    }

    @Test
    void should_contain_auth_token_expiration_rule() {
        given()
        .when()
            .get("/api/v1/business-rules")
        .then()
            .statusCode(200)
            .body("ruleName", hasItem("auth_token_expiration"));
    }

    @Test
    void should_expose_yaml_config_for_each_rule() {
        given()
        .when()
            .get("/api/v1/business-rules")
        .then()
            .statusCode(200)
            .body("config", everyItem(notNullValue()))
            .body("config.appointment.slot.minMinutes", everyItem(equalTo(30)))
            .body("config.auth.token.expirationMs", everyItem(equalTo(86400000)));
    }

    @Test
    void should_access_without_token() {
        given()
        .when()
            .get("/api/v1/business-rules")
        .then()
            .statusCode(200)
            .body("$", not(empty()));
    }

    @Test
    void should_expose_public_endpoints_as_json_array() {
        Object publicEndpoints = authConfig().get("publicEndpoints");

        assertThat(publicEndpoints, notNullValue());
        assertThat(publicEndpoints, instanceOf(List.class));

        @SuppressWarnings("unchecked")
        List<Object> endpoints = (List<Object>) publicEndpoints;
        assertThat(endpoints, hasSize(5));
        assertThat(endpoints, hasItems("/api/v1/auth/**", "/api/v1/business-rules/**"));
        for (Object endpoint : endpoints) {
            assertThat((String) endpoint, startsWith("/api/v1/"));
        }
    }

    @Test
    void should_expose_auth_scalar_config_without_type_drift() {
        Map<String, Object> auth = authConfig();

        Map<String, Object> password = child(auth, "password");
        Map<String, Object> token = child(auth, "token");

        assertThat(((Number) password.get("minLength")).intValue(), is(8));
        assertThat(password.get("algorithm"), is("BCrypt"));
        assertThat(((Number) token.get("expirationMs")).longValue(), is(86400000L));
        assertThat(token.get("algorithm"), is("HMAC-SHA256"));
    }

    private String descriptionOf(String ruleName) {
        List<Map<String, Object>> rules = given()
        .when()
            .get("/api/v1/business-rules")
        .then()
            .statusCode(200)
            .extract().jsonPath().getList("$");
        return rules.stream()
                .filter(rule -> ruleName.equals(rule.get("ruleName")))
                .map(rule -> (String) rule.get("description"))
                .findFirst()
                .orElse(null);
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> authConfig() {
        List<Map<String, Object>> rules = given()
        .when()
            .get("/api/v1/business-rules")
        .then()
            .statusCode(200)
            .extract().jsonPath().getList("$");
        for (Map<String, Object> rule : rules) {
            Object config = rule.get("config");
            if (!(config instanceof Map<?, ?> configMap)) continue;
            Object auth = configMap.get("auth");
            if (auth instanceof Map<?, ?> authMap) {
                return (Map<String, Object>) authMap;
            }
        }
        throw new AssertionError("no rule exposes config.auth");
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> child(Map<String, Object> parent, String key) {
        Object value = parent.get(key);
        assertThat(value, instanceOf(Map.class));
        return (Map<String, Object>) value;
    }
}
