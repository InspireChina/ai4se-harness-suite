package com.consultation.adapter.rest;

import com.consultation.adapter.rest.dto.AddFavoriteRequest;
import com.consultation.adapter.rest.dto.AgreementConsentRequest;
import com.consultation.adapter.rest.dto.AgreementConsentResponse;
import com.consultation.adapter.rest.dto.FavoriteResponse;
import com.consultation.adapter.rest.dto.MeResponse;
import com.consultation.adapter.rest.dto.ProfileResponse;
import com.consultation.adapter.rest.dto.UpdateProfileRequest;
import com.consultation.application.service.AgreementAppService;
import com.consultation.application.service.FavoriteAppService;
import com.consultation.application.service.ProfileAppService;
import com.consultation.infrastructure.security.SecurityUtils;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 「我的」相关接口：资料、收藏、协议同意。
 */
@RestController
@RequestMapping("/api/v1/me")
@RequiredArgsConstructor
public class MeController {

    private final ProfileAppService profileAppService;
    private final FavoriteAppService favoriteAppService;
    private final AgreementAppService agreementAppService;

    @GetMapping
    public ResponseEntity<MeResponse> me() {
        return ResponseEntity.ok(profileAppService.getMe(SecurityUtils.currentUserId()));
    }

    @PutMapping("/profile")
    public ResponseEntity<ProfileResponse> updateProfile(@Valid @RequestBody UpdateProfileRequest request) {
        return ResponseEntity.ok(profileAppService.updateProfile(
                SecurityUtils.currentUserId(),
                request.getNickname(),
                request.getAvatarUrl(),
                request.getEmail(),
                request.getCityCode(),
                request.getLocale()));
    }

    @GetMapping("/favorites")
    public ResponseEntity<List<FavoriteResponse>> listFavorites() {
        return ResponseEntity.ok(favoriteAppService.list(SecurityUtils.currentUserId()));
    }

    @PostMapping("/favorites")
    public ResponseEntity<FavoriteResponse> addFavorite(@Valid @RequestBody AddFavoriteRequest request) {
        return ResponseEntity.ok(favoriteAppService.add(SecurityUtils.currentUserId(), request.getConsultantId()));
    }

    @DeleteMapping("/favorites/{consultantId}")
    public ResponseEntity<Void> removeFavorite(@PathVariable String consultantId) {
        favoriteAppService.remove(SecurityUtils.currentUserId(), consultantId);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/agreements")
    public ResponseEntity<List<AgreementConsentResponse>> listAgreements() {
        return ResponseEntity.ok(agreementAppService.list(SecurityUtils.currentUserId()));
    }

    @PostMapping("/agreements")
    public ResponseEntity<AgreementConsentResponse> consent(@Valid @RequestBody AgreementConsentRequest request,
                                                             HttpServletRequest httpRequest) {
        return ResponseEntity.ok(agreementAppService.consent(
                SecurityUtils.currentUserId(),
                request.getAgreementType(),
                request.getAgreementVersion(),
                resolveSourceIp(httpRequest)));
    }

    private String resolveSourceIp(HttpServletRequest request) {
        String forwarded = request.getHeader("X-Forwarded-For");
        if (forwarded != null && !forwarded.isBlank()) {
            return forwarded.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
