package com.consultation.adapter.rest;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class HealthControllerTest {

    @Test
    void should_return_up_when_get_health() {
        var body = new HealthController().health();
        assertEquals("UP", body.get("status"));
    }
}
