package com.consultation.infrastructure.consultant;

import com.consultation.domain.service.DisplayableConsultantPort;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.LinkedHashSet;
import java.util.Set;

/**
 * 「可展示咨询师」Stub 实现：白名单 ID 视为可展示。
 *
 * <p>CDC / COB 落地后由真实实现替换（consultant.displayable-ids 配置项）。</p>
 */
@Component
public class StubDisplayableConsultantPort implements DisplayableConsultantPort {

    private final Set<String> displayableIds = new LinkedHashSet<>();

    public StubDisplayableConsultantPort(@Value("${consultant.displayable-ids:}") String csv) {
        if (csv != null && !csv.isBlank()) {
            for (String id : csv.split(",")) {
                String trimmed = id.trim();
                if (!trimmed.isEmpty()) {
                    displayableIds.add(trimmed);
                }
            }
        }
    }

    @Override
    public boolean isDisplayable(String consultantId) {
        return consultantId != null && displayableIds.contains(consultantId.trim());
    }
}
