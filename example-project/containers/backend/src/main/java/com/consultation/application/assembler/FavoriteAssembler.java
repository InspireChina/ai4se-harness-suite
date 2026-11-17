package com.consultation.application.assembler;

import com.consultation.adapter.rest.dto.FavoriteResponse;
import com.consultation.domain.aggregate.FavoriteConsultant;
import org.springframework.stereotype.Component;

@Component
public class FavoriteAssembler {

    public FavoriteResponse toResponse(FavoriteConsultant favorite) {
        if (favorite == null) {
            return null;
        }
        return FavoriteResponse.builder()
                .id(favorite.getId())
                .consultantId(favorite.getConsultantId())
                .createdAt(favorite.getCreatedAt())
                .build();
    }
}
