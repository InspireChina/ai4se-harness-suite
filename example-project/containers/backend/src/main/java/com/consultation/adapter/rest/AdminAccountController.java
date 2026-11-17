package com.consultation.adapter.rest;

import com.consultation.adapter.rest.dto.AccountResponse;
import com.consultation.adapter.rest.dto.DisableAccountRequest;
import com.consultation.application.service.AdminAccountAppService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 管理端账号操作（需 ROLE_ADMIN）。
 */
@RestController
@RequestMapping("/api/v1/admin/accounts")
@RequiredArgsConstructor
public class AdminAccountController {

    private final AdminAccountAppService adminAccountAppService;

    @PostMapping("/{id}/disable")
    public ResponseEntity<AccountResponse> disable(@PathVariable String id,
                                                   @Valid @RequestBody DisableAccountRequest request) {
        return ResponseEntity.ok(adminAccountAppService.disable(id, request.getReason()));
    }

    @PostMapping("/{id}/enable")
    public ResponseEntity<AccountResponse> enable(@PathVariable String id) {
        return ResponseEntity.ok(adminAccountAppService.enable(id));
    }
}
