package com.consultation.adapter.rest;

import com.consultation.TestBase;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;

class AdminAccountControllerTest extends TestBase {

    private static final String PHONE = "13800138000";

    @Test
    void should_disable_account_and_invalidate_existing_session() {
        String userToken = loginBySms(PHONE);
        String accountId = currentAccountId(userToken);
        String adminToken = loginAdmin();

        given().header("Authorization", "Bearer " + adminToken)
                .contentType(ContentType.JSON)
                .body(Map.of("reason", "违规内容"))
                .post("/api/v1/admin/accounts/" + accountId + "/disable")
                .then().statusCode(200)
                .body("status", equalTo("DISABLED"))
                .body("disabledReason", equalTo("违规内容"))
                .body("phone", equalTo("138****8000"));

        given().header("Authorization", "Bearer " + userToken)
                .get("/api/v1/me")
                .then().statusCode(401)
                .body("errorCode", equalTo("UNAUTHORIZED"));
    }

    @Test
    void should_reject_login_for_disabled_account() {
        String userToken = loginBySms(PHONE);
        String accountId = currentAccountId(userToken);
        String adminToken = loginAdmin();

        given().header("Authorization", "Bearer " + adminToken)
                .contentType(ContentType.JSON)
                .body(Map.of("reason", "违规内容"))
                .post("/api/v1/admin/accounts/" + accountId + "/disable")
                .then().statusCode(200);

        String code = requestSmsCode(PHONE);
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", PHONE, "code", code))
                .post("/api/v1/auth/sms/login")
                .then().statusCode(409)
                .body("errorCode", equalTo("BUSINESS_CONFLICT"))
                .body("errorMessage", startsWith("账号不可用"));
    }

    @Test
    void should_enable_account_again() {
        String userToken = loginBySms(PHONE);
        String accountId = currentAccountId(userToken);
        String adminToken = loginAdmin();

        given().header("Authorization", "Bearer " + adminToken)
                .contentType(ContentType.JSON)
                .body(Map.of("reason", "违规内容"))
                .post("/api/v1/admin/accounts/" + accountId + "/disable")
                .then().statusCode(200);

        given().header("Authorization", "Bearer " + adminToken)
                .post("/api/v1/admin/accounts/" + accountId + "/enable")
                .then().statusCode(200)
                .body("status", equalTo("ACTIVE"));

        String newToken = loginBySms(PHONE);
        given().header("Authorization", "Bearer " + newToken)
                .get("/api/v1/me")
                .then().statusCode(200)
                .body("account.id", notNullValue());
    }

    @Test
    void should_return_403_when_non_admin_tries_to_disable_account() {
        String userToken = loginBySms(PHONE);
        String accountId = currentAccountId(userToken);

        given().header("Authorization", "Bearer " + userToken)
                .contentType(ContentType.JSON)
                .body(Map.of("reason", "违规内容"))
                .post("/api/v1/admin/accounts/" + accountId + "/disable")
                .then().statusCode(403);
    }

    @Test
    void should_return_401_when_admin_endpoint_called_without_token() {
        given().contentType(ContentType.JSON)
                .body(Map.of("reason", "违规内容"))
                .post("/api/v1/admin/accounts/any-id/disable")
                .then().statusCode(401);
    }

    @Test
    void should_return_400_when_disable_reason_is_missing() {
        String adminToken = loginAdmin();

        given().header("Authorization", "Bearer " + adminToken)
                .contentType(ContentType.JSON)
                .body(Map.of())
                .post("/api/v1/admin/accounts/any-id/disable")
                .then().statusCode(400)
                .body("errorCode", equalTo("VALIDATION_ERROR"));
    }

    @Test
    void should_return_400_when_account_does_not_exist() {
        String adminToken = loginAdmin();

        given().header("Authorization", "Bearer " + adminToken)
                .contentType(ContentType.JSON)
                .body(Map.of("reason", "违规内容"))
                .post("/api/v1/admin/accounts/not-exist-id/disable")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }
}
