package com.example.customer;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/customers")
public class CustomerController {

    private final CustomerService customerService;

    public CustomerController(CustomerService customerService) {
        this.customerService = customerService;
    }

    @GetMapping("/{customerId}/profile")
    public ResponseEntity<CustomerProfile> getProfile(@PathVariable String customerId) {
        return ResponseEntity.ok(customerService.loadProfile(customerId));
    }

    @PostMapping("/{customerId}/protect")
    public ResponseEntity<ProtectionResult> protectSensitiveFields(
            @PathVariable String customerId,
            @RequestBody ProtectCustomerRequest request) {
        return ResponseEntity.ok(customerService.protectCustomer(customerId, request));
    }
}
