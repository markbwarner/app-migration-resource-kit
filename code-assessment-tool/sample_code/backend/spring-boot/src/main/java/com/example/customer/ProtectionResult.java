package com.example.customer;

import java.util.List;

public record ProtectionResult(String customerId, List<String> protectedFields) {
}
