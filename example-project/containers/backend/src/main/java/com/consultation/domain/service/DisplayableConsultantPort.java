package com.consultation.domain.service;

/**
 * 咨询师「可展示」判定端口。本期由 ACC 提供 Stub 实现，CDC/COB 落地后替换为真实实现。
 */
public interface DisplayableConsultantPort {

    boolean isDisplayable(String consultantId);
}
