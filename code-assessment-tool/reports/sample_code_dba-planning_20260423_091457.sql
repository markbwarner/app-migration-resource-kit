-- DBA planning SQL generated from jdbc_candidate files
--
-- Notes:
-- 1. DESCRIBE is common in MySQL-family tools and some SQL consoles.
--    Oracle SQL*Plus-style environments often use DESC, and some databases
--    require INFORMATION_SCHEMA or catalog queries instead.
-- 2. The max-length checks below use LENGTH(column), which is valid in
--    Oracle, PostgreSQL, and MySQL. SQL Server typically uses LEN(column).

-- Table: claim_review
-- Source files: ClaimReviewService.cs
describe claim_review;

-- Max current lengths for sensitive columns in claim_review
select
  max(length(home_address)) as max_home_address_length,
  max(length(household_id)) as max_household_id_length,
  max(length(member_email)) as max_member_email_length,
  max(length(salary_amount)) as max_salary_amount_length
from claim_review;

-- Table: customer_profile
-- Source files: CustomerService.cs, CustomerService.java
describe customer_profile;

-- Max current lengths for sensitive columns in customer_profile
select
  max(length(date_of_birth)) as max_date_of_birth_length,
  max(length(email)) as max_email_length,
  max(length(first_name)) as max_first_name_length,
  max(length(last_name)) as max_last_name_length,
  max(length(phone_number)) as max_phone_number_length
from customer_profile;

-- Table: customer_event_audit
-- Source files: CustomerEventProcessor.java
describe customer_event_audit;

-- Max current lengths for sensitive columns in customer_event_audit
select
  max(length(email)) as max_email_length,
  max(length(home_address)) as max_home_address_length,
  max(length(phone_number)) as max_phone_number_length,
  max(length(ssn)) as max_ssn_length
from customer_event_audit;

-- Table: billing_account
-- Source files: BillingRepository.java
describe billing_account;

-- Max current lengths for sensitive columns in billing_account
select
  max(length(account_number)) as max_account_number_length,
  max(length(billing_address)) as max_billing_address_length,
  max(length(card_number)) as max_card_number_length,
  max(length(cvv)) as max_cvv_length,
  max(length(routing_number)) as max_routing_number_length
from billing_account;

-- Table: customer_audit
-- Source files: customer-service.js
describe customer_audit;

-- Max current lengths for sensitive columns in customer_audit
select
  max(length(date_of_birth)) as max_date_of_birth_length,
  max(length(email)) as max_email_length,
  max(length(phone_number)) as max_phone_number_length,
  max(length(ssn)) as max_ssn_length
from customer_audit;

-- Table: household_member_profile
-- Source files: HouseholdRepository.java
describe household_member_profile;

-- Max current lengths for sensitive columns in household_member_profile
select
  max(length(account_number)) as max_account_number_length,
  max(length(home_address)) as max_home_address_length,
  max(length(household_id)) as max_household_id_length,
  max(length(primary_email)) as max_primary_email_length,
  max(length(salary_amount)) as max_salary_amount_length
from household_member_profile;
