# Sample Code Corpus

This folder contains synthetic sample applications to exercise the scanner.

## Included patterns

- Front end React component referencing PII and calling REST endpoints
- Front end Angular component referencing payment PII and posting to a back end
- Node.js UI gateway making REST calls with PII payloads
- Java Spring Boot service using REST plus JDBC/SQL
- .NET API using `HttpClient` plus `SqlConnection`
- Node.js service using Kafka and PostgreSQL
- Python FastAPI service using REST and SQL updates
- Go HTTP handler using SQL statements
- Java Kafka consumer using REST plus `PreparedStatement`
- Vector-search style code in Python and Node.js
- JDBC-only repository code that is a strong JDBC-driver candidate
- Customer-specific alias examples such as `acctNbr`, `accntNbr`, `householdNbr`, and `hhId`
- Spring controller to service to repository flow for ownership correlation
- DTO/supporting-model samples that should be labeled `supporting_model`
- React and Node.js proxy samples with routes that correlate to likely backend owners
- Additional route-aligned React, Node.js, and .NET claim-review samples for easier endpoint correlation demos

## Suggested scan

```powershell
python app.py E:\codex\work\migration\sample_code --json-out E:\codex\work\migration\sample_code\sample-report.json
```

## What you should expect

- Front-end files should be classified as `frontend` or `frontend_with_service_calls`
- Java and .NET service files should be classified as back-end or back-end with data access
- JDBC-heavy files should show higher JDBC-driver candidate counts
- CRDP REST orchestration files should show higher code-change candidate counts
- React `HouseholdMemberScreen.tsx` should correlate to `HouseholdController.java`
- `HouseholdProtectionRequest.java` and `HouseholdMemberProfile.java` should behave like supporting DTO/model files
- `claims-proxy.js` should look like `frontend_reference_only` while `claims-service.js` looks like the more likely backend/data owner
- `claims-api-proxy.js` and `ClaimReviewScreen.tsx` should correlate more directly to `/api/claims/...` back-end owners
- `.NET ClaimReviewController.cs` should look like an API owner, while `ClaimReviewService.cs` should look like the stronger data-access/JDBC-style owner
