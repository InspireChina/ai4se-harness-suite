package com.consultation.infrastructure.persistence.converter;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;

/**
 * 领域时间（Instant，UTC 语义）与库内时间（DATETIME，Asia/Shanghai）互转。
 */
public final class TimeConverter {

    public static final ZoneId ZONE = ZoneId.of("Asia/Shanghai");

    private TimeConverter() {
    }

    public static LocalDateTime toLocalDateTime(Instant instant) {
        return instant == null ? null : LocalDateTime.ofInstant(instant, ZONE);
    }

    public static Instant toInstant(LocalDateTime localDateTime) {
        return localDateTime == null ? null : localDateTime.atZone(ZONE).toInstant();
    }
}
