package com.example.customer;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
public class CustomerService {

    private final JdbcTemplate jdbcTemplate;
    private final RestTemplate restTemplate;

    public CustomerService(JdbcTemplate jdbcTemplate, RestTemplate restTemplate) {
        this.jdbcTemplate = jdbcTemplate;
        this.restTemplate = restTemplate;
    }

    public CustomerProfile loadProfile(String customerId) {
        return jdbcTemplate.queryForObject(
                """
                select customer_id, first_name, last_name, email, phone_number, date_of_birth,
                       ssn, home_address, tax_id
                from customer_profile
                where customer_id = ?
                """,
                (rs, rowNum) -> new CustomerProfile(
                        rs.getString("customer_id"),
                        rs.getString("first_name"),
                        rs.getString("last_name"),
                        rs.getString("email"),
                        rs.getString("phone_number"),
                        rs.getString("date_of_birth"),
                        rs.getString("ssn"),
                        rs.getString("home_address"),
                        rs.getString("tax_id")),
                customerId
        );
    }

    public ProtectionResult protectCustomer(String customerId, ProtectCustomerRequest request) {
        CrdpProtectRequest crdpProtectRequest = new CrdpProtectRequest(
                request.email(),
                request.phoneNumber(),
                request.dateOfBirth(),
                request.ssn(),
                request.homeAddress());

        CrdpProtectResponse response = restTemplate.postForObject(
                "https://ciphertrust.example.com/v1/protect/customer",
                crdpProtectRequest,
                CrdpProtectResponse.class
        );

        jdbcTemplate.update(
                """
                update customer_profile
                set email = ?, phone_number = ?, date_of_birth = ?, ssn = ?, home_address = ?
                where customer_id = ?
                """,
                response.protectedEmail(),
                response.protectedPhoneNumber(),
                response.protectedDateOfBirth(),
                response.protectedSsn(),
                response.protectedHomeAddress(),
                customerId
        );

        return new ProtectionResult(customerId, List.of("email", "phoneNumber", "dateOfBirth", "ssn", "homeAddress"));
    }
}
