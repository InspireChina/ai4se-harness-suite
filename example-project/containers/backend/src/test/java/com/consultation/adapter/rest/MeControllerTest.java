package com.consultation.adapter.rest;

import com.consultation.TestBase;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.notNullValue;

class MeControllerTest extends TestBase {

    private static final String PHONE = "13800138000";
    private static final String CONSULTANT_ID = "stub-consultant-001";

    @Test
    void should_return_current_account_and_profile_when_get_me() {
        String token = loginBySms(PHONE);

        given().header("Authorization", "Bearer " + token)
                .get("/api/v1/me")
                .then().statusCode(200)
                .body("account.id", notNullValue())
                .body("account.status", equalTo("ACTIVE"))
                .body("account.phone", equalTo(PHONE))
                .body("profile.accountId", notNullValue());
    }

    @Test
    void should_return_401_when_get_me_without_token() {
        given().get("/api/v1/me")
                .then().statusCode(401);
    }

    @Test
    void should_return_401_when_update_profile_without_token() {
        given().contentType(ContentType.JSON)
                .body(Map.of("nickname", "阿宁"))
                .put("/api/v1/me/profile")
                .then().statusCode(401);
    }

    @Test
    void should_update_own_profile_and_read_it_back() {
        String token = loginBySms(PHONE);
        Map<String, String> body = new HashMap<>();
        body.put("nickname", "新昵称");
        body.put("email", "ning@example.com");
        body.put("cityCode", "310000");
        body.put("locale", "zh-CN");

        given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(body)
                .put("/api/v1/me/profile")
                .then().statusCode(200)
                .body("nickname", equalTo("新昵称"))
                .body("email", equalTo("ning@example.com"))
                .body("cityCode", equalTo("310000"));

        given().header("Authorization", "Bearer " + token)
                .get("/api/v1/me")
                .then().statusCode(200)
                .body("profile.nickname", equalTo("新昵称"))
                .body("profile.email", equalTo("ning@example.com"));
    }

    @Test
    void should_return_400_when_nickname_is_too_short() {
        String token = loginBySms(PHONE);

        given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("nickname", "a"))
                .put("/api/v1/me/profile")
                .then().statusCode(400)
                .body("errorCode", equalTo("VALIDATION_ERROR"));
    }

    @Test
    void should_favorite_and_unfavorite_idempotently() {
        String token = loginBySms(PHONE);

        String favoriteId = given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("consultantId", CONSULTANT_ID))
                .post("/api/v1/me/favorites")
                .then().statusCode(200)
                .body("consultantId", equalTo(CONSULTANT_ID))
                .extract().path("id");

        given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("consultantId", CONSULTANT_ID))
                .post("/api/v1/me/favorites")
                .then().statusCode(200)
                .body("id", equalTo(favoriteId));

        given().header("Authorization", "Bearer " + token)
                .get("/api/v1/me/favorites")
                .then().statusCode(200)
                .body("$", hasSize(1));

        given().header("Authorization", "Bearer " + token)
                .delete("/api/v1/me/favorites/" + CONSULTANT_ID)
                .then().statusCode(204);

        given().header("Authorization", "Bearer " + token)
                .get("/api/v1/me/favorites")
                .then().statusCode(200)
                .body("$", hasSize(0));

        given().header("Authorization", "Bearer " + token)
                .delete("/api/v1/me/favorites/" + CONSULTANT_ID)
                .then().statusCode(204);
    }

    @Test
    void should_return_400_when_favorite_unknown_consultant() {
        String token = loginBySms(PHONE);

        given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("consultantId", "not-displayable"))
                .post("/api/v1/me/favorites")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }

    @Test
    void should_record_agreement_consent_idempotently() {
        String token = loginBySms(PHONE);

        String consentId = given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("agreementType", "service", "agreementVersion", "v1"))
                .post("/api/v1/me/agreements")
                .then().statusCode(200)
                .body("agreementType", equalTo("service"))
                .body("agreementVersion", equalTo("v1"))
                .body("consentedAt", notNullValue())
                .body("sourceIp", notNullValue())
                .extract().path("id");

        given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("agreementType", "privacy", "agreementVersion", "v1"))
                .post("/api/v1/me/agreements")
                .then().statusCode(200)
                .body("agreementType", equalTo("privacy"));

        given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("agreementType", "service", "agreementVersion", "v1"))
                .post("/api/v1/me/agreements")
                .then().statusCode(200)
                .body("id", equalTo(consentId));

        given().header("Authorization", "Bearer " + token)
                .get("/api/v1/me/agreements")
                .then().statusCode(200)
                .body("$", hasSize(2));
    }

    @Test
    void should_return_400_when_agreement_type_is_invalid() {
        String token = loginBySms(PHONE);

        given().header("Authorization", "Bearer " + token)
                .contentType(ContentType.JSON)
                .body(Map.of("agreementType", "unknown", "agreementVersion", "v1"))
                .post("/api/v1/me/agreements")
                .then().statusCode(400)
                .body("errorCode", equalTo("PARAM_ERROR"));
    }

    @Test
    void should_keep_favorites_private_between_accounts() {
        String firstToken = loginBySms(PHONE);
        given().header("Authorization", "Bearer " + firstToken)
                .contentType(ContentType.JSON)
                .body(Map.of("consultantId", CONSULTANT_ID))
                .post("/api/v1/me/favorites")
                .then().statusCode(200);

        String secondToken = loginBySms("13900139000");

        given().header("Authorization", "Bearer " + secondToken)
                .get("/api/v1/me/favorites")
                .then().statusCode(200)
                .body("$", hasSize(0));
    }
}
