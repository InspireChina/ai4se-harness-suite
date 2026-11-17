package com.consultation.infrastructure.persistence.converter;

import com.consultation.domain.aggregate.UserProfile;
import com.consultation.infrastructure.persistence.po.UserProfilePO;
import org.springframework.stereotype.Component;

@Component
public class UserProfileConverter {

    public UserProfile toDomain(UserProfilePO po) {
        if (po == null) {
            return null;
        }
        return UserProfile.builder()
                .accountId(po.getAccountId())
                .nickname(po.getNickname())
                .avatarUrl(po.getAvatarUrl())
                .email(po.getEmail())
                .cityCode(po.getCityCode())
                .locale(po.getLocale())
                .updatedAt(TimeConverter.toInstant(po.getUpdatedAt()))
                .build();
    }

    public UserProfilePO toPO(UserProfile profile) {
        if (profile == null) {
            return null;
        }
        UserProfilePO po = new UserProfilePO();
        po.setAccountId(profile.getAccountId());
        po.setNickname(profile.getNickname());
        po.setAvatarUrl(profile.getAvatarUrl());
        po.setEmail(profile.getEmail());
        po.setCityCode(profile.getCityCode());
        po.setLocale(profile.getLocale());
        po.setUpdatedAt(TimeConverter.toLocalDateTime(profile.getUpdatedAt()));
        return po;
    }
}
