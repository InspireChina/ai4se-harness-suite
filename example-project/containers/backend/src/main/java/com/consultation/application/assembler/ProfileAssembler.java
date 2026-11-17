package com.consultation.application.assembler;

import com.consultation.adapter.rest.dto.ProfileResponse;
import com.consultation.domain.aggregate.UserProfile;
import org.springframework.stereotype.Component;

@Component
public class ProfileAssembler {

    public ProfileResponse toResponse(UserProfile profile) {
        if (profile == null) {
            return null;
        }
        return ProfileResponse.builder()
                .accountId(profile.getAccountId())
                .nickname(profile.getNickname())
                .avatarUrl(profile.getAvatarUrl())
                .email(profile.getEmail())
                .cityCode(profile.getCityCode())
                .locale(profile.getLocale())
                .updatedAt(profile.getUpdatedAt())
                .build();
    }
}
