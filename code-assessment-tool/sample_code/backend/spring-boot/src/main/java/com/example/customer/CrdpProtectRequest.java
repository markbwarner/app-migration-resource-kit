package com.example.customer;

public record CrdpProtectRequest(
        String email,
        String phoneNumber,
        String dateOfBirth,
        String ssn,
        String homeAddress) {
}
