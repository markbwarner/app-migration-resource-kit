package com.example.household;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
public class HouseholdProtectionService {

    private final HouseholdRepository householdRepository;
    private final RestTemplate restTemplate;

    public HouseholdProtectionService(HouseholdRepository householdRepository, RestTemplate restTemplate) {
        this.householdRepository = householdRepository;
        this.restTemplate = restTemplate;
    }

    public List<HouseholdMemberProfile> loadMembers(String householdId) {
        return householdRepository.loadMembers(householdId);
    }

    public ProtectionResult protectMembers(String householdId, HouseholdProtectionRequest request) {
        HouseholdProtectionPayload payload = new HouseholdProtectionPayload(
                request.householdId(),
                request.primaryEmail(),
                request.salaryAmount(),
                request.accntNbr(),
                request.homeAddress());

        HouseholdProtectionPayload protectedPayload = restTemplate.postForObject(
                "https://ciphertrust.example.com/v1/protect/household",
                payload,
                HouseholdProtectionPayload.class
        );

        householdRepository.updateProtectedMemberData(
                householdId,
                protectedPayload.primaryEmail(),
                protectedPayload.salaryAmount(),
                protectedPayload.accntNbr(),
                protectedPayload.homeAddress()
        );

        return new ProtectionResult(
                householdId,
                List.of("primaryEmail", "salaryAmount", "accntNbr", "homeAddress")
        );
    }
}
