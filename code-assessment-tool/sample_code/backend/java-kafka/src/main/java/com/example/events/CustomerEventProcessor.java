package com.example.events;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;

@Component
public class CustomerEventProcessor {

    private final RestTemplate restTemplate;
    private final DataSource dataSource;

    public CustomerEventProcessor(RestTemplate restTemplate, DataSource dataSource) {
        this.restTemplate = restTemplate;
        this.dataSource = dataSource;
    }

    @KafkaListener(topics = "customer-registration")
    public void handleCustomerRegistration(ConsumerRecord<String, String> record) throws Exception {
        String eventPayload = record.value();

        String protectedPayload = restTemplate.postForObject(
                "https://ciphertrust.example.com/v1/protect/event",
                eventPayload,
                String.class
        );

        try (Connection connection = dataSource.getConnection();
             PreparedStatement preparedStatement = connection.prepareStatement(
                     "insert into customer_event_audit(customer_id, email, phone_number, ssn, home_address) values (?, ?, ?, ?, ?)")) {
            preparedStatement.setString(1, "C123");
            preparedStatement.setString(2, "{\"email\":\"alice@example.com\"}");
            preparedStatement.setString(3, "{\"phoneNumber\":\"555-1212\"}");
            preparedStatement.setString(4, "{\"ssn\":\"123-45-6789\"}");
            preparedStatement.setString(5, protectedPayload);
            preparedStatement.executeUpdate();
        }
    }
}
