package com.consultation.application.service;

import com.consultation.adapter.rest.dto.FavoriteResponse;
import com.consultation.application.assembler.FavoriteAssembler;
import com.consultation.domain.aggregate.FavoriteConsultant;
import com.consultation.domain.repository.FavoriteConsultantRepository;
import com.consultation.domain.service.DisplayableConsultantPort;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

/**
 * 收藏用例（R-CREATE-004 幂等收藏 / R-DELETE-001 仅收藏人可取消）。
 */
@Service
@RequiredArgsConstructor
public class FavoriteAppService {

    private final FavoriteConsultantRepository favoriteRepository;
    private final DisplayableConsultantPort displayableConsultantPort;
    private final FavoriteAssembler favoriteAssembler;

    public List<FavoriteResponse> list(String accountId) {
        return favoriteRepository.findByAccountId(accountId).stream()
                .map(favoriteAssembler::toResponse)
                .toList();
    }

    /**
     * 收藏咨询师（幂等）：已收藏直接返回既有记录。
     */
    @Transactional
    public FavoriteResponse add(String accountId, String consultantId) {
        if (consultantId == null || consultantId.isBlank()) {
            throw new IllegalArgumentException("咨询师ID不能为空");
        }
        String trimmed = consultantId.trim();
        if (!displayableConsultantPort.isDisplayable(trimmed)) {
            throw new IllegalArgumentException("咨询师不存在或不可展示");
        }
        return favoriteRepository.findByAccountIdAndConsultantId(accountId, trimmed)
                .map(favoriteAssembler::toResponse)
                .orElseGet(() -> {
                    FavoriteConsultant created = FavoriteConsultant.builder()
                            .id(UUID.randomUUID().toString())
                            .accountId(accountId)
                            .consultantId(trimmed)
                            .createdAt(Instant.now())
                            .build();
                    return favoriteAssembler.toResponse(favoriteRepository.save(created));
                });
    }

    /**
     * 取消收藏（幂等）：未收藏也按成功处理。
     */
    @Transactional
    public void remove(String accountId, String consultantId) {
        if (consultantId == null || consultantId.isBlank()) {
            throw new IllegalArgumentException("咨询师ID不能为空");
        }
        favoriteRepository.deleteByAccountIdAndConsultantId(accountId, consultantId.trim());
    }
}
