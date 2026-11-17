package com.consultation;

import com.consultation.config.ResetDbService;
import com.consultation.infrastructure.sms.MockSmsSender;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;

import java.util.Map;

import static io.restassured.RestAssured.given;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public abstract class TestBase {

    /** 平台种子管理员（与 src/test/resources/application.yml 的 seed.admin.* 一致）。 */
    protected static final String ADMIN_PHONE = "13900000000";
    protected static final String ADMIN_PASSWORD = "Admin@12345";

    @LocalServerPort
    int port;

    @Autowired
    ResetDbService resetDbService;

    @Autowired
    MockSmsSender mockSmsSender;

    @BeforeEach
    void setUp() {
        RestAssured.port = port;
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
        resetDbService.resetAll();
    }

    /** 发送验证码并返回 Mock 通道实际送达的验证码。 */
    protected String requestSmsCode(String phone) {
        given().contentType(ContentType.JSON)
                .body(Map.of("phone", phone))
                .post("/api/v1/auth/sms/send")
                .then().statusCode(204);
        return mockSmsSender.lastCode();
    }

    /** 验证码登录 / 注册，返回 token。 */
    protected String loginBySms(String phone) {
        String code = requestSmsCode(phone);
        return given().contentType(ContentType.JSON)
                .body(Map.of("phone", phone, "code", code))
                .post("/api/v1/auth/sms/login")
                .then().statusCode(200)
                .extract().path("token");
    }

    /** 管理员密码登录，返回 token。 */
    protected String loginAdmin() {
        return given().contentType(ContentType.JSON)
                .body(Map.of("phone", ADMIN_PHONE, "password", ADMIN_PASSWORD))
                .post("/api/v1/auth/admin/login")
                .then().statusCode(200)
                .extract().path("token");
    }

    /** 当前登录账号的 ID。 */
    protected String currentAccountId(String token) {
        return given().header("Authorization", "Bearer " + token)
                .get("/api/v1/me")
                .then().statusCode(200)
                .extract().path("account.id");
    }
}
