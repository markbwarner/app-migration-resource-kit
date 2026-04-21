package com.example.household;

public record HouseholdProtectionPayload(
        String householdId,
        String primaryEmail,
        String salaryAmount,
        String accntNbr,
        String homeAddress) {
}
