package com.consultation.adapter.rest;

import com.consultation.TestBase;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

class DataDictionaryControllerTest extends TestBase {

    @Test
    void should_list_all_data_dictionary_types() {
        given()
        .when()
            .get("/api/v1/data-dictionaries")
        .then()
            .statusCode(200)
            .body("$", not(empty()))
            .body("$", hasSize(5))
            .body("typeName", everyItem(not(isEmptyOrNullString())))
            .body("description", everyItem(not(isEmptyOrNullString())))
            .body("items", everyItem(hasSize(greaterThan(0))));
    }

    @Test
    void should_get_data_dictionary_by_type() {
        given()
        .when()
            .get("/api/v1/data-dictionaries/USER_ROLE")
        .then()
            .statusCode(200)
            .body("typeName", equalTo("USER_ROLE"))
            .body("description", not(isEmptyOrNullString()))
            .body("items.code", hasItems("ROLE_USER", "ROLE_ADMIN"))
            .body("items.description", everyItem(not(isEmptyOrNullString())));
    }

    @Test
    void should_get_data_dictionary_by_type_ignoring_case() {
        given()
        .when()
            .get("/api/v1/data-dictionaries/user_role")
        .then()
            .statusCode(200)
            .body("typeName", equalTo("USER_ROLE"))
            .body("items.code", hasItems("ROLE_USER", "ROLE_ADMIN"));
    }

    @Test
    void should_list_all_appointment_status_codes() {
        given()
        .when()
            .get("/api/v1/data-dictionaries/APPOINTMENT_STATUS")
        .then()
            .statusCode(200)
            .body("typeName", equalTo("APPOINTMENT_STATUS"))
            .body("items.code", hasItems("PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"));
    }

    @Test
    void should_fail_for_unknown_dictionary_type() {
        given()
        .when()
            .get("/api/v1/data-dictionaries/NOT_EXIST")
        .then()
            .statusCode(400)
            .body("errorCode", equalTo("PARAM_ERROR"))
            .body("errorMessage", containsString("字典类型不存在"))
            .body("data", nullValue());
    }
}
