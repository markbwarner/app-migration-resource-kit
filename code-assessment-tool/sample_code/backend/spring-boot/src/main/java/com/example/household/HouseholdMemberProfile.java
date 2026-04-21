package com.example.household;

public record HouseholdMemberProfile(
        String householdId,
        String primaryEmail,
        String salaryAmount,
        String accntNbr,
        String homeAddress) {
}
