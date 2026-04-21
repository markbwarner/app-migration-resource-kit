package com.example.customer;

public record ProtectCustomerRequest(
        String email,
        String phoneNumber,
        String dateOfBirth,
        String ssn,
        String homeAddress) {
}
