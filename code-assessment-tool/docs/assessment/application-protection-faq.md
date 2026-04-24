# Application Protection FAQ

This FAQ is intended to help customers understand where protection and reveal APIs are usually best implemented, how to interpret the scanner output, and how to use the reports for project planning.

## 1. In a multi-tier application, where is the best place to implement protect and reveal APIs?

In most enterprise multi-tier applications, the best default integration point is usually the shared back-end service layer, not the UI layer.

That is because the back end typically owns:

- business rules
- data validation
- transformation logic
- shared service endpoints
- database, Kafka, file, and integration access
- centralized auditing and authorization decisions

The UI often references sensitive fields, but it is usually not the best long-term control point when a reusable service layer already exists.

## 2. Why is the back end usually the better protection point?

Back-end implementation usually provides:

- centralized enforcement across multiple channels
- less duplication across React, Angular, mobile, Node.js UI gateways, and other clients
- better alignment with network boundaries and firewall zones
- stronger consistency for protect, reveal, masking, and auditing behavior
- easier maintenance when policies change
- better regression-test coverage at the service and integration layer

## 3. Does that mean the UI never needs protection or reveal API changes?

No.

Some UI or client-tier applications may still be valid integration points, especially when:

- the app is internal and directly invokes enterprise systems
- there is no meaningful shared middle tier
- the client already behaves like the real integration layer
- the client performs important business logic before data leaves the app
- local masking, redaction, or workflow requirements justify early protection

The key question is not whether the UI references sensitive data. The key question is which layer truly owns the data-handling decision.

## 4. How should customers think about different application types?

Use this general rule:

- customer-facing multi-tier app
  - shared back-end web services are usually the preferred implementation point
- internal multi-tier app
  - back-end shared services are still usually preferred if they exist
- internal client app acting as the real integration layer
  - the client app may be a valid protection point
- batch, Kafka, analytics, ETL, or headless service
  - the service or integration layer is usually the correct protection point

## 5. What value does `frontend_to_backend_correlations` provide?

`frontend_to_backend_correlations` helps answer this question:

"Even if the front end references sensitive fields, which back-end files are the more likely real change owners?"

That is useful because many customers initially assume that every front-end sensitive-field reference implies front-end code change scope. In many cases, the real implementation work is concentrated in a smaller set of shared back-end APIs or services.

The value of this section is:

- it helps reduce false scope
- it highlights likely ownership chains from UI to service layer
- it gives architects and developers a better starting point for implementation review
- it supports discussions about where CRDP REST work is most likely to belong

It is important to understand what it does not do:

- it is not a true runtime dependency graph
- it is not proof that one file definitely calls another
- it is a heuristic correlation based on route patterns, payload fields, and naming overlap

The practical use is:

- treat the front-end file as context
- treat the correlated back-end file as the more likely review target
- confirm that target with other fields such as `likely_change_owner`, `recommended_change_action`, and `ownership_confidence`

## 6. What does `likely_change_target` mean?

`likely_change_target` is a convenience flag.

- `true`
  - the file looks like a likely primary review target
- `false`
  - the file is more likely contextual, front-end-only, or a supporting model

This is one of the easiest fields to use for first-pass filtering.

## 7. What does `recommended_change_action` mean?

`recommended_change_action` gives a search-friendly recommendation for what kind of review the file most likely needs.

Typical values:

- `review_crdp_rest_change`
  - likely back-end service or orchestration review target
- `review_data_access_change`
  - likely persistence or integration-layer review target
- `review_jdbc_substitution`
  - likely JDBC-driver substitution candidate
- `frontend_reference_only`
  - likely contextual front-end reference, not the main implementation point
- `supporting_model_only`
  - likely DTO, request, response, or model file
- `needs_manual_review`
  - current evidence is not strong enough for a confident recommendation

## 8. What is the easiest way to find the code most likely to need changes?

The easiest starting point is the `likely-change-targets.csv` file.

A common working filter is:

- `likely_change_target = True`

Then sort or filter by:

- `recommended_change_action`
- `ownership_confidence`
- `complexity_score`
- `code_change_candidate_count`

That usually gives teams a much smaller and more realistic review set than reading every file-level finding.

## 9. What is the difference between `likely_change_owner` and `role_in_flow`?

These two fields answer different questions.

- `likely_change_owner`
  - who probably needs to change
- `role_in_flow`
  - what this file does in the sensitive-data path

Examples:

- `frontend_reference_only` plus `collects_and_sends`
  - UI file gathers data and sends it onward, but is probably not the primary implementation point
- `backend_logic_owner` plus `receives_and_transforms`
  - service receives sensitive fields and likely owns business logic or CRDP orchestration
- `jdbc_candidate` plus `persists_or_publishes`
  - file writes sensitive data to a database or publishes it and may be a JDBC-driver candidate

## 10. How should customers interpret `ownership_confidence`?

`ownership_confidence` is a heuristic score from `0.0` to `1.0`.

Higher values mean the scanner found stronger evidence for the classification.

It is best used for prioritization, not as proof.

Good practical use:

- review higher-confidence targets first
- use lower-confidence results as candidates for manual review

## 11. What do `backend_owner_confidence` and `endpoint_correlation_score` mean?

- `backend_owner_confidence`
  - how strongly the file looks like a back-end implementation owner
- `endpoint_correlation_score`
  - how strongly the file appears correlated to related files through routes, endpoints, and payload overlap

These are especially useful when explaining why a front-end reference does not necessarily mean a front-end implementation change.

## 12. What do `code_change_candidate_count` and `jdbc_candidate_count` mean?

- `code_change_candidate_count`
  - count of indicators suggesting a file may require application-code review or modification
- `jdbc_candidate_count`
  - count of indicators suggesting a JDBC-driver approach may reduce direct code changes

These are heuristic counts, not final estimates, but they are useful for ranking likely review effort.

## 13. Does adding up `totals_by_category` equal the total number of matches?

Usually yes.

`totals_by_category` is the count of emitted match records by category, and those category totals roll up to `total_pii_matches`.

Important nuance:

- this is not the same as the number of unique fields
- one identifier can produce more than one category match if both built-in and custom patterns apply

## 14. What does the complexity score really mean?

The complexity score is a planning metric, not an engineering-hours estimate.

It is intended to compare files by likely migration and testing impact.

In general:

- complexity increases with:
  - more sensitive-field matches
  - larger files
  - more service and integration behavior
  - more likely application-code change points
- complexity decreases when:
  - the file looks front-end-only
  - a JDBC-driver approach may reduce code changes

It is best used for:

- scoping
- sequencing
- prioritization
- testing discussions

## 15. What is the best DBA handoff output?

Two outputs are particularly useful for DBAs:

- `likely-change-targets.csv`
  - especially the columns:
    - `jdbc_tables`
    - `sensitive_columns`
    - `sensitive_tables`
- `dba-planning.sql`
  - generated with `--sql-out`

These help DBAs identify:

- which tables appear in JDBC-candidate flows
- which sensitive columns should be reviewed
- which columns may need width validation before rollout

## 16. What does the DBA planning SQL file do?

For each detected JDBC-candidate table, the SQL file generates:

- a `describe table_name;` statement
- a `select max(length(column)) ... from table_name;` statement for the sensitive columns

This supports two planning tasks:

- validate current table and column definitions
- compare current maximum data length against expected future width needs

For example, if tokenization metadata may add 7 bytes, DBAs can compare:

- current max stored length
- current declared column width
- expected future width requirement

## 17. Is the generated SQL portable across all databases?

Not completely.

The current SQL is designed as a practical planning handoff, but syntax varies by database.

General guidance:

- `length(column)`
  - valid in Oracle, PostgreSQL, and MySQL-family databases
- `len(column)`
  - usually required in SQL Server
- `describe table_name;`
  - common in MySQL-family tools
  - Oracle tools often use `desc`
  - some platforms require catalog queries instead

So the SQL file is best treated as a DBA planning starter, not a guaranteed universal script.

## 18. What outputs are best for Excel, Power Query, or BI tools?

Recommended outputs:

- `likely-change-targets.csv`
  - best for focused triage and working sessions
- `pii-file-reports.csv`
  - best for wider file-level analysis, pivots, and charts
- `pii-file-reports.json`
  - good if you want file-level JSON only
- `pii-impact-summary.json`
  - good for executive dashboards or automation

## 19. What are the most useful questions a customer should ask after running the scanner?

- Which files are true likely change owners versus contextual references?
- How many front-end references collapse into a smaller set of shared back-end owners?
- Which files are strongest JDBC-driver candidates?
- Which tables and sensitive columns should be handed to DBAs first?
- Which files are high-complexity and should be reviewed earlier?
- Which routes and payloads indicate shared service ownership?

## 20. What is the simplest customer message?

The most important message is:

The question is not just where sensitive data appears. The more important question is which application layer truly owns the data-handling decision. In most enterprise multi-tier applications, that owner is usually the shared back-end service or integration layer, not the UI screen.
