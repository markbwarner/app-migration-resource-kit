package com.example.customer;

public record CrdpProtectResponse(
        String protectedEmail,
        String protectedPhoneNumber,
        String protectedDateOfBirth,
        String protectedSsn,
        String protectedHomeAddress) {
}
