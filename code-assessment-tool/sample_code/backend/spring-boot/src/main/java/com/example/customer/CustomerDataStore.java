package com.example.customer;

import org.springframework.stereotype.Repository;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.Table;

@Repository
public class CustomerDataStore {

    @PersistenceContext
    private EntityManager entityManager;

    public CustomerSecureRecord upsert(CustomerSecureRecord record) {
        return entityManager.merge(record);
    }

    public CustomerSecureRecord loadByCustomerId(String customerId) {
        return entityManager.find(CustomerSecureRecord.class, customerId);
    }

    @Entity
    @Table(name = "customer_secure_profile")
    public static class CustomerSecureRecord {

        @Column(name = "customer_id")
        private String customerId;

        @Column(name = "primary_email")
        private String primaryEmail;

        @Column(name = "phone_number")
        private String phoneNumber;

        @Column(name = "home_address")
        private String homeAddress;

        @Column(name = "date_of_birth")
        private String dateOfBirth;

        @Column(name = "household_id")
        private String householdId;

        @Column(name = "salary_amount")
        private String salaryAmount;

        public String getCustomerId() {
            return customerId;
        }

        public void setCustomerId(String customerId) {
            this.customerId = customerId;
        }

        public String getPrimaryEmail() {
            return primaryEmail;
        }

        public void setPrimaryEmail(String primaryEmail) {
            this.primaryEmail = primaryEmail;
        }

        public String getPhoneNumber() {
            return phoneNumber;
        }

        public void setPhoneNumber(String phoneNumber) {
            this.phoneNumber = phoneNumber;
        }

        public String getHomeAddress() {
            return homeAddress;
        }

        public void setHomeAddress(String homeAddress) {
            this.homeAddress = homeAddress;
        }

        public String getDateOfBirth() {
            return dateOfBirth;
        }

        public void setDateOfBirth(String dateOfBirth) {
            this.dateOfBirth = dateOfBirth;
        }

        public String getHouseholdId() {
            return householdId;
        }

        public void setHouseholdId(String householdId) {
            this.householdId = householdId;
        }

        public String getSalaryAmount() {
            return salaryAmount;
        }

        public void setSalaryAmount(String salaryAmount) {
            this.salaryAmount = salaryAmount;
        }
    }
}
