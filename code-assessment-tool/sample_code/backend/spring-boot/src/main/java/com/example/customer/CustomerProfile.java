package com.example.customer;

public record CustomerProfile(
        String customerId,
        String firstName,
        String lastName,
        String email,
        String phoneNumber,
        String dateOfBirth,
        String ssn,
        String homeAddress,
        String taxId) {
}
