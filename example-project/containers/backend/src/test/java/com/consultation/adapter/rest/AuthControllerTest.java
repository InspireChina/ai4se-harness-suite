package com.consultation.adapter.rest;

import com.consultation.TestBase;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.jupiter.api.Assertions.assertEquals;

class AuthControllerTest extends TestBase {

    private static final String PHONE = "13800138000";

    @Test
    void should_return_204_when_send_sms_code() {
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", PHONE))
                .post("/api/v1/auth/sms/send")
                .then().statusCode(204);
    }

    @Test
    void should_register_new_account_with_user_role_when_sms_login() {
        String code = requestSmsCode(PHONE);

        given().contentType(ContentType.JSON)
                .body(Map.of("phone", PHONE, "code", code, "nickname", "阿宁"))
                .post("/api/v1/auth/sms/login")
                .then().statusCode(200)
                .body("token", notNullValue())
                .body("account.id", notNullValue())
                .body("account.status", equalTo("ACTIVE"))
                .body("account.roles", contains("USER"))
                .body("profile.nickname", equalTo("阿宁"));
    }

    @Test
    void should_not_create_duplicate_account_when_login_again() {
        String firstToken = loginBySms(PHONE);
        String firstAccountId = currentAccountId(firstToken);

        String secondToken = loginBySms(PHONE);

        assertEquals(firstAccountId, currentAccountId(secondToken));
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", PHONE))
                .post("/api/v1/auth/sms/send")
                .then().statusCode(204);
    }

    @Test
    void should_return_400_when_verification_code_is_wrong() {
        requestSmsCode(PHONE);

        given().contentType(ContentType.JSON)
                .body(Map.of("phone", PHONE, "code", "000000"))
                .post("/api/v1/auth/sms/login")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"))
                .body("errorMessage", startsWith("验证码"));
    }

    @Test
    void should_return_400_when_phone_format_is_invalid() {
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", "12345", "code", "123456"))
                .post("/api/v1/auth/sms/login")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }

    @Test
    void should_return_400_when_send_sms_code_with_invalid_phone() {
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", "12345"))
                .post("/api/v1/auth/sms/send")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }

    @Test
    void should_return_400_when_verification_code_is_missing() {
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", PHONE))
                .post("/api/v1/auth/sms/login")
                .then().statusCode(400)
                .body("errorCode", equalTo("VALIDATION_ERROR"));
    }

    @Test
    void should_login_admin_with_password() {
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", ADMIN_PHONE, "password", ADMIN_PASSWORD))
                .post("/api/v1/auth/admin/login")
                .then().statusCode(200)
                .body("token", notNullValue())
                .body("account.roles", contains("ADMIN"));
    }

    @Test
    void should_return_400_when_admin_password_is_wrong() {
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", ADMIN_PHONE, "password", "wrong-password"))
                .post("/api/v1/auth/admin/login")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }

    @Test
    void should_return_400_when_admin_account_does_not_exist() {
        Map<String, String> body = new HashMap<>();
        body.put("phone", "13700137000");
        body.put("password", ADMIN_PASSWORD);

        given().contentType(ContentType.JSON)
                .body(body)
                .post("/api/v1/auth/admin/login")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }

    @Test
    void should_reject_sms_login_for_non_admin_account() {
        loginBySms(PHONE);

        given().contentType(ContentType.JSON)
                .body(Map.of("phone", PHONE, "password", ADMIN_PASSWORD))
                .post("/api/v1/auth/admin/login")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }
}
