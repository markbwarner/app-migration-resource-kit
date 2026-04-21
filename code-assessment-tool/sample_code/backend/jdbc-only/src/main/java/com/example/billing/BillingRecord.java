package com.example.billing;

public record BillingRecord(
        String accountNumber,
        String routingNumber,
        String cardNumber,
        String cvv,
        String billingAddress) {
}
