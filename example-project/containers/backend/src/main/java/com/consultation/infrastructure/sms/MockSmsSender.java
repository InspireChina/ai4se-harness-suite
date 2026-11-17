package com.consultation.infrastructure.sms;

import com.consultation.domain.service.SmsSender;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.concurrent.atomic.AtomicReference;

/**
 * 本地 Mock 短信通道：真短信供应商接入前使用（归 PLT）。
 *
 * <p>固定验证码 {@code sms.mock.fixed-code} 供本地联调与 E2E 使用；生产环境必须留空。</p>
 */
@Slf4j
@Component
public class MockSmsSender implements SmsSender {

    private final AtomicReference<String> lastCode = new AtomicReference<>();
    private final String fixedCode;
    private final boolean exposeCode;

    public MockSmsSender(@Value("${sms.mock.fixed-code:}") String fixedCode,
                          @Value("${sms.mock.expose-code:true}") boolean exposeCode) {
        this.fixedCode = fixedCode == null ? "" : fixedCode.trim();
        this.exposeCode = exposeCode;
    }

    @Override
    public String send(String phone, String code) {
        String delivered = fixedCode.isEmpty() ? code : fixedCode;
        if (exposeCode) {
            lastCode.set(delivered);
        }
        log.debug("[MockSmsSender] phone={} code={}", mask(phone), delivered);
        return delivered;
    }

    /** 最近一次发送的验证码（仅本地联调 / 测试使用）。 */
    public String lastCode() {
        return lastCode.get();
    }

    /** 固定验证码（为空表示随机生成）。 */
    public String fixedCode() {
        return fixedCode;
    }

    private String mask(String phone) {
        if (phone == null || phone.length() < 7) {
            return "***";
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }
}
