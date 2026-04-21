package com.example.household;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/households")
public class HouseholdController {

    private final HouseholdProtectionService householdProtectionService;

    public HouseholdController(HouseholdProtectionService householdProtectionService) {
        this.householdProtectionService = householdProtectionService;
    }

    @GetMapping("/{householdId}/members")
    public ResponseEntity<List<HouseholdMemberProfile>> getMembers(@PathVariable String householdId) {
        return ResponseEntity.ok(householdProtectionService.loadMembers(householdId));
    }

    @PostMapping("/{householdId}/protect")
    public ResponseEntity<ProtectionResult> protectMembers(
            @PathVariable String householdId,
            @RequestBody HouseholdProtectionRequest request) {
        return ResponseEntity.ok(householdProtectionService.protectMembers(householdId, request));
    }
}
