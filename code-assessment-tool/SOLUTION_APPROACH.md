# Solution Approach

## Recommended architecture

Keep the first version simple and explainable:

1. Source crawler
2. PII detector
3. Application layer classifier
4. Migration impact estimator
5. Report generator

### 1. Source crawler

Scan a customer-provided root directory and include common source and config file types:

- Java, Kotlin, C#, Python, JavaScript, TypeScript
- SQL, properties, YAML, XML, JSON
- JSP and HTML where UI payload references may exist

Exclude common generated or vendor folders:

- `node_modules`
- `dist`
- `target`
- `build`
- `.git`

### 2. PII detector

Use code-aware identifier scanning as the primary method:

- built-in identifier heuristics for fields like `customerSsn`, `birthDate`, and `accountNumber`
- customer alias lists for names like `acctNbr`, `accntNbr`, `householdNbr`, and `hhId`

Optionally add Presidio for:

- literals
- comments
- sample payloads
- test data

This keeps the core solution deterministic, maintainable, and portable to a future Java implementation.

### 3. Application layer classifier

Classify files using lightweight evidence:

- Front end:
  - React, Angular, Vue, TypeScript UI files
  - `fetch`, `axios`, Apollo, GraphQL client calls
- Back end:
  - Spring Boot annotations
  - Express, Flask, FastAPI route handlers
  - service and controller classes
- Data access:
  - JDBC, SQL, JPA, repositories, data sources
- Integration:
  - Kafka, MQ, queues, listeners, event payloads

The point is not perfect static analysis. The point is to quickly separate likely UI references from likely migration touchpoints.

### 4. Migration impact estimator

Estimate likely migration path using rules:

- Front-end only file with REST calls:
  - likely low direct CRDP code impact
  - note that back-end review is still required
- Back-end or service file with PII and transformation/orchestration logic:
  - likely CRDP code-change candidate
- Data-access or JDBC-heavy file with PII:
  - likely JDBC-driver candidate
- Mixed file:
  - flag for manual review

### 5. Report generator

Generate:

- line-level findings
- per-file category summaries
- file classification
- JDBC-driver candidate count
- code-change candidate count
- complexity score
- notes for architects and delivery teams

## Best technology choice

For version 1, the best choice is:

- code heuristics + customer aliases

Not:

- AI-only analysis

### Why

- Lower cost
- No dependency on model prompts for the primary scan
- Easier to justify to security and architecture teams
- Repeatable and explainable
- Easier to run on customer premises
- Easier to port to Java or .NET later

Presidio can remain an optional add-on in the Python version, but it should not be the architectural center of the solution.

## Where AI helps later

AI is still useful, but as a second step:

- summarize migration impact by application or domain
- explain likely change patterns
- group findings into work packages
- draft migration estimates and assumptions
- highlight architectural unknowns for manual follow-up

## Suggested output fields

For each finding:

- application name
- file path
- line number
- matched attribute
- PII category
- detection type: `presidio` or `keyword`
- confidence
- likely layer
- likely migration path: `jdbc_driver`, `code_change`, `review`

For each file:

- total PII matches
- categories found
- REST/service markers
- SQL/JDBC markers
- complexity score
- complexity rating
- rationale

## Effort estimation factors

Use these for the initial migration estimate:

- Number of applications in scope
- Number of repositories
- Number of files with confirmed PII touchpoints
- Number of back-end service files that transform, validate, or map PII
- Number of data-access modules using JDBC or SQL
- Number of APIs that accept or return protected data
- Number of event streams or queues carrying protected data
- Number of databases, schemas, and tables involved
- Whether JDBC substitution can be done centrally or per app
- Whether tokenization, format preservation, or re-identification is required
- Performance and latency constraints
- Test automation maturity
- UAT and regression scope
- Release coordination across teams
- Non-production environments needed for proof-of-value and validation

Use these for ongoing support estimates:

- Number of protected applications in production
- Frequency of schema and API changes
- New PII field onboarding volume
- Key rotation and policy changes
- Monitoring and alerting requirements
- Dependency upgrades for drivers and client libraries
- Production incident model and support window
- Audit/reporting expectations

## Recommended delivery model

1. Run automated scan
2. Review findings with customer architects
3. Confirm system-of-record touchpoints
4. Separate JDBC-driver opportunities from true code-change work
5. Build migration backlog by application and interface
6. Estimate implementation, testing, cutover, and support

## Practical guidance

Do not try to make version 1 perfect.

The main goal is to reduce ambiguity quickly:

- where PII exists
- which files are probably just UI references
- which files are likely real migration touchpoints
- where JDBC can reduce code changes

That is enough to scope the work and have a much better customer conversation.
