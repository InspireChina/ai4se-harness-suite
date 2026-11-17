package com.consultation.infrastructure.persistence.converter;

import com.consultation.domain.aggregate.FavoriteConsultant;
import com.consultation.infrastructure.persistence.po.FavoriteConsultantPO;
import org.springframework.stereotype.Component;

@Component
public class FavoriteConsultantConverter {

    public FavoriteConsultant toDomain(FavoriteConsultantPO po) {
        if (po == null) {
            return null;
        }
        return FavoriteConsultant.builder()
                .id(po.getId())
                .accountId(po.getAccountId())
                .consultantId(po.getConsultantId())
                .createdAt(TimeConverter.toInstant(po.getCreatedAt()))
                .build();
    }

    public FavoriteConsultantPO toPO(FavoriteConsultant favorite) {
        if (favorite == null) {
            return null;
        }
        FavoriteConsultantPO po = new FavoriteConsultantPO();
        po.setId(favorite.getId());
        po.setAccountId(favorite.getAccountId());
        po.setConsultantId(favorite.getConsultantId());
        po.setCreatedAt(TimeConverter.toLocalDateTime(favorite.getCreatedAt()));
        return po;
    }
}
