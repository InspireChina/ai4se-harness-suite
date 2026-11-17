package com.consultation.domain.service;

/**
 * 短信发送端口。本期实现为本地 Mock，真短信通道归 PLT。
 *
 * <p>返回实际送达的验证码：Mock 固定码场景下返回固定值，调用方按返回值落摘要。</p>
 */
public interface SmsSender {

    String send(String phone, String code);
}
