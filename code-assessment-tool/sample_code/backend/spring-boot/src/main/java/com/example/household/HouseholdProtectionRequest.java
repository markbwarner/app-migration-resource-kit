package com.example.household;

public record HouseholdProtectionRequest(
        String householdId,
        String primaryEmail,
        String salaryAmount,
        String accntNbr,
        String homeAddress) {
}
