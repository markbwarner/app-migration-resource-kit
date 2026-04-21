package com.example.household;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class HouseholdRepository {

    private final JdbcTemplate jdbcTemplate;

    public HouseholdRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<HouseholdMemberProfile> loadMembers(String householdId) {
        return jdbcTemplate.query(
                """
                select household_id, primary_email, salary_amount, account_number, home_address
                from household_member_profile
                where household_id = ?
                """,
                (rs, rowNum) -> new HouseholdMemberProfile(
                        rs.getString("household_id"),
                        rs.getString("primary_email"),
                        rs.getString("salary_amount"),
                        rs.getString("account_number"),
                        rs.getString("home_address")),
                householdId
        );
    }

    public void updateProtectedMemberData(
            String householdId,
            String primaryEmail,
            String salaryAmount,
            String accntNbr,
            String homeAddress) {
        jdbcTemplate.update(
                """
                update household_member_profile
                set primary_email = ?, salary_amount = ?, account_number = ?, home_address = ?
                where household_id = ?
                """,
                primaryEmail,
                salaryAmount,
                accntNbr,
                homeAddress,
                householdId
        );
    }
}
