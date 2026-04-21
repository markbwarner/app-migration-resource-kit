package com.example.billing;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class BillingRepository {

    private final DataSource dataSource;

    public BillingRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public BillingRecord loadBillingRecord(String accountNumber) throws Exception {
        try (Connection connection = dataSource.getConnection();
             PreparedStatement preparedStatement = connection.prepareStatement(
                     "select account_number, routing_number, card_number, cvv, billing_address from billing_account where account_number = ?")) {
            preparedStatement.setString(1, accountNumber);
            ResultSet resultSet = preparedStatement.executeQuery();
            resultSet.next();
            return new BillingRecord(
                    resultSet.getString("account_number"),
                    resultSet.getString("routing_number"),
                    resultSet.getString("card_number"),
                    resultSet.getString("cvv"),
                    resultSet.getString("billing_address"));
        }
    }
}
