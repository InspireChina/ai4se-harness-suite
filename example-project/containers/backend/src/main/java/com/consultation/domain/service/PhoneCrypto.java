package com.consultation.domain.service;

/**
 * 手机号加解密端口。实现位于 infrastructure（本期为 AES-GCM）。
 */
public interface PhoneCrypto {

    /** 摘要（不可逆），用于唯一查询与等值比较。 */
    String hash(String plaintext);

    /** 加密（可逆），用于库内存储并仅向本人解密展示。 */
    String encrypt(String plaintext);

    /** 解密。 */
    String decrypt(String ciphertext);
}
