# Application Code Sensitive Data Scanner Assessment Tool

## Page 1: Find The Real Migration Touchpoints Faster

The Application Code Sensitive Data Scanner Assessment Tool helps customers find sensitive field references in source code, determine which files are likely true change owners, and estimate where a Thales JDBC driver approach may reduce application changes.

This is not a traditional data-discovery tool searching for real account numbers or actual SSNs in production data. It is a source-code assessment tool designed for practical migration planning.

It helps answer questions such as:

- Where do fields like `ssn`, `dateOfBirth`, `email`, `acctNbr`, `householdId`, and `salaryAmount` appear in code?
- Are those references only in front-end files, or in the back-end and data-access layers that are more likely to require change?
- Which files look like JDBC substitution candidates versus CRDP REST code-change candidates?
- How large is the likely delivery and testing effort?

### Top Benefits

- **Scope clarity**
  - Distinguishes broad source-code awareness from likely implementation ownership.
- **Faster planning**
  - Reduces guesswork for project planning, workshops, and rough-order estimates.
- **Actionable output**
  - Gives developers, architects, and DevOps teams repeatable evidence through console and JSON reports.

### Why This Matters

In many multi-tier applications:

- React, Angular, or Node.js front ends reference sensitive data for screens and payloads
- Spring Boot, .NET, Python, Go, or Node.js services implement business logic
- JDBC, SQL, Kafka, vector-search, and integration layers move data to systems of record

Without code-level analysis, teams often overestimate front-end impact and underestimate the back-end and integration work that actually drives complexity.

## Page 2: Executive Summary And How The Scanner Works

The scanner is built for source code. It extracts identifier-like tokens, normalizes naming styles, compares them to built-in and customer-defined aliases, and then applies architecture and ownership heuristics.

Example:

- raw token: `accntNbr`
- normalized token: `accnt_nbr`
- configured alias: `accnt_nbr`
- result: `CUSTOM_ACCOUNT_NUMBER`

This works well across:

- camelCase
- PascalCase
- snake_case
- customer abbreviations such as `acctNbr`, `accntNbr`, `householdNbr`, and `hhId`

### What The Scanner Produces

- line-level findings with line number, attribute, and category
- per-file summaries by category
- likely file classification:
  - `frontend`
  - `frontend_with_service_calls`
  - `backend`
  - `backend_with_data_access`
  - `data_access`
- ownership analysis:
  - `frontend_reference_only`
  - `backend_logic_owner`
  - `data_access_owner`
  - `jdbc_candidate`
  - `supporting_model`
- flow-role analysis such as:
  - `collects_and_sends`
  - `receives_and_transforms`
  - `persists_or_publishes`
- route and endpoint correlation
- REST, SQL, and JDBC markers
- potential JDBC-driver candidate counts
- potential code-change candidate counts
- a complexity score
- progress indicators during scanning
- optional JSON report output

### Why Ownership Analysis Matters

The scanner can now show the difference between:

- a front-end file that references five sensitive elements but only sends them to another tier
- a controller or service file that appears to own the API or business-logic change
- a repository or SQL-heavy file that may be a JDBC substitution candidate
- a DTO or request/response model that contains field names but is not the true implementation point

In this context, `DTO` means `Data Transfer Object`. It is usually a simple class or record used to carry data between layers, for example:

- a request body sent from a front end to an API
- a response payload returned by a service
- a model shape passed between controller, service, and repository layers

A DTO usually describes the data structure, not the business logic. That is why a DTO file may contain many sensitive field names while still not being the primary CRDP or JDBC implementation point.

This helps customers move from "where is sensitive data mentioned?" to "what actually needs to change?"

### Executive Summary Output

The executive summary is now the primary output because it gives architects, developers, project planners, and DBAs a faster way to understand where effort is likely to concentrate.

Current sample corpus results:

```text
Root path: E:\codex\work\migration\sample_code
Files scanned: 42
Files with PII indicators: 38
Total PII matches: 511
Potential JDBC-driver candidates: 70
Potential code-change candidates: 209

Executive summary:
  Likely change owner summary:
    - supporting_model: 17
    - frontend_reference_only: 9
    - jdbc_candidate: 9
    - backend_logic_owner: 3
  Role in flow summary:
    - supporting_model: 17
    - collects_and_sends: 9
    - persists_or_publishes: 9
    - receives_and_transforms: 3
  Complexity distribution:
    - low: 6
    - medium: 12
    - high: 20
  Front-end to back-end correlations:
    - CustomerProfile.tsx -> CustomerController.java (score 0.8)
    - HouseholdMemberScreen.tsx -> HouseholdController.java (score 0.8)
  Back-end to data-access correlations:
    - HouseholdProtectionService.java -> HouseholdRepository.java (score 0.67)
  Likely JDBC tables and sensitive columns:
    - customer_profile: date_of_birth, email, first_name, last_name, phone_number (files 2)
    - household_member_profile: account_number, home_address, household_id, primary_email, salary_amount (files 1)
```

This summary helps teams quickly answer:

- which files are likely true change owners
- which files are only front-end references or supporting models
- which back-end flows correlate to data-access layers
- which JDBC tables and sensitive columns should be handed to DBAs early

## Page 3: Metrics, Complexity, And Customer Outcome

### Key Metrics

- **Files scanned**
  - Total files analyzed in scope.
- **Files with indicators**
  - Files containing at least one sensitive field reference.
- **Total matches**
  - Line-level findings across the codebase.
- **Potential JDBC-driver candidates**
  - Areas where SQL and JDBC indicators suggest lower-impact migration potential.
- **Potential code-change candidates**
  - Files more likely to require CRDP REST orchestration or transformation work.
- **Ownership fields**
  - Evidence about likely change owner, role in flow, related files, and endpoint correlation.
- **Executive summary correlations**
  - Highlights likely front-end to back-end and back-end to data-access relationships without requiring teams to read every file-level finding.
- **DBA handoff summary**
  - Groups likely JDBC tables and sensitive columns so database teams can validate scope and prepare for migration activity sooner.

### Complexity Index

The complexity index is a planning aid that considers:

- lines of code
- number of sensitive-field matches
- likely code-change touchpoints
- REST or service-call markers
- SQL and JDBC markers
- whether JDBC substitution may reduce impact
- whether the file appears front-end only, back-end logic, data access, or supporting model

Complexity ratings:

- `Low`
  - usually limited touchpoints or mostly front-end-only awareness
- `Medium`
  - bounded implementation effort with manageable testing scope
- `High`
  - multiple sensitive fields, integrations, and significant regression impact

### Good Fit For

- CRDP migration discovery workshops
- JDBC versus CRDP REST planning
- portfolio scoping and application grouping
- developer impact analysis
- DevOps reporting and repeatable repository scans
- onboarding new customer-specific aliases
- DBA planning and schema-readiness review
- executive and project-planning readouts using the executive summary

### Customer Outcome

Instead of debating migration scope from diagrams alone, customers can review concrete evidence showing:

- where sensitive fields appear
- which files are likely front-end references only
- which files are likely API or business-logic owners
- which files are likely data-access or JDBC candidates
- which files are only supporting DTO or model definitions
- which front-end files correlate to likely back-end owners
- which service files correlate to likely data-access owners
- which JDBC tables and sensitive columns should be validated by DBAs
- where testing and delivery effort are likely to concentrate

The result is faster scoping, clearer project planning, better DBA preparation, and a more practical conversation about Thales CRDP REST protection versus JDBC-based protection.
