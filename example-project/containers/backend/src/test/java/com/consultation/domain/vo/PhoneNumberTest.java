package com.consultation.domain.vo;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class PhoneNumberTest {

    @Test
    void should_normalize_phone_with_spaces_and_dashes() {
        assertEquals("13800138000", PhoneNumber.of(" 138-0013 8000 ").value());
    }

    @Test
    void should_reject_invalid_phone_format() {
        assertThrows(IllegalArgumentException.class, () -> PhoneNumber.of("12345"));
        assertThrows(IllegalArgumentException.class, () -> PhoneNumber.of("23800138000"));
        assertThrows(IllegalArgumentException.class, () -> PhoneNumber.of(""));
        assertThrows(IllegalArgumentException.class, () -> PhoneNumber.of(null));
    }

    @Test
    void should_keep_same_value_after_normalization() {
        assertEquals(PhoneNumber.of("13800138000").value(), PhoneNumber.of("138 0013 8000").value());
    }
}
