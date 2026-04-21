# PII Code Impact Scanner

This Python application scans a source tree for likely PII references, reports line-level matches, classifies files as front end or back end, and estimates whether Thales CipherTrust REST Data Protection (CRDP) changes are more likely to require:

- application code changes
- a Thales JDBC driver approach with lower code impact

## What it does

- Detects likely PII references in code using built-in code-aware keyword heuristics for identifiers like `ssn`, `dob`, `email`, `customerName`, and `accountNumber`
- Supports customer-defined alias patterns such as `acctNbr`, `accntNbr`, `householdNbr`, and `hhId`
- Optionally supports Microsoft Presidio for literals, comments, sample payloads, and embedded text when enabled
- Reports:
  - file path
  - line number
  - matched attribute or literal
  - PII category
- Produces per-file summaries by category
- Produces a report-level summary of likely JDBC table names and sensitive columns to support DBA planning
- Classifies files into likely layers:
  - `frontend`
  - `frontend_with_service_calls`
  - `backend`
  - `backend_with_data_access`
  - `data_access`
  - `unknown`
- Counts architecture hints:
  - REST/web service call markers
  - SQL markers
  - JDBC markers
  - endpoint/controller markers
- Estimates migration path:
  - potential JDBC-driver candidates
  - potential code-change candidates
- Derives a simple complexity score to help scope migration effort

## Why Presidio is optional

For this use case, the core problem is code-reference discovery, not text PII detection.

Most of the important matches are things like:

- variable names
- DTO fields
- SQL column names
- JSON property names
- method parameters
- customer-specific aliases

Examples:

- `customerSsn`
- `dateOfBirth`
- `acctNbr`
- `accntNbr`
- `householdId`

Those are best handled by code-aware identifier scanning, not by Presidio.

Presidio can still help in a secondary role for:

- comments
- sample payloads
- test data
- config files
- embedded example JSON

That is why Presidio is disabled by default and only enabled with `--use-presidio`.

## Why Presidio alone is not enough

Presidio is very useful for detecting PII values in text, comments, payload samples, test data, and literals. But source code often refers to PII through identifiers rather than real values, for example:

- `customerSsn`
- `dateOfBirth`
- `employeeEmail`
- `taxId`

Those are important migration touchpoints, and pure NLP often misses them. This scanner intentionally combines Presidio with lightweight code heuristics to keep the solution practical and not over-engineered.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The scanner runs without Presidio. Presidio is optional and only needed if you want the `--use-presidio` mode.

## Usage

```powershell
python app.py E:\source\customer-app --json-out E:\source\customer-app\pii-impact-report.json
```

By default the scanner prints progress messages while it runs so long scans do not appear stalled.
By default the console output now shows an executive summary only. Use `--include-file-reports` if you want the detailed file-by-file findings printed as well.
By default the JSON output also contains the executive summary only. Use `--json-include-file-reports` if you want the detailed file-by-file findings included in the JSON report.

If you want to suppress progress output:

```powershell
python app.py E:\source\customer-app --quiet
```

If you want to see the exact matched hint terms that contributed to file classification:

```powershell
python app.py E:\source\customer-app --include-file-reports --show-hint-breakdown
```

Optional Presidio pass:

```powershell
python app.py E:\source\customer-app --use-presidio
```

Optional excludes:

```powershell
python app.py E:\source\customer-app --exclude-dir coverage --exclude-dir generated
```

Custom customer-defined patterns:

```powershell
python app.py E:\source\customer-app --custom-patterns E:\codex\work\migration\custom-patterns.example.json
```

If you want customer-defined categories to replace the built-in keyword category for the same identifier:

```powershell
python app.py E:\source\customer-app --custom-patterns E:\codex\work\migration\custom-patterns.example.json --custom-patterns-override-defaults
```

If you want the detailed file-level report output:

```powershell
python app.py E:\source\customer-app --include-file-reports
```

If you want the JSON report to include the detailed file-by-file findings:

```powershell
python app.py E:\source\customer-app --json-out E:\source\customer-app\pii-impact-report.json --json-include-file-reports
```
## Example output

```text
File: E:\source\customer-app\src\main\java\com\acme\CustomerDao.java
  Layer: backend_with_data_access (confidence 0.86)
  LOC: 180, REST calls: 0, SQL markers: 8, JDBC markers: 6
  Potential JDBC-driver candidates: 6, potential code-change candidates: 2
  Complexity: medium (score 18.5)
  Summary by category:
    - EMAIL_ADDRESS: 2
    - US_SSN: 4
  Matches:
    - line 42: customerSsn -> US_SSN [keyword, 0.72]
    - line 57: email -> EMAIL_ADDRESS [keyword, 0.72]
```

## Recommended design

The best low-complexity design is a two-stage scanner:

1. Static scan using code heuristics and custom aliases
2. Rule-based impact inference for architecture layer and migration path

That gives you explainable output, repeatable results, and a report that solution architects can review with customers.

## Should you use Presidio, AI, or both?

Best practical answer:

- Use code heuristics and custom aliases as the primary engine
- Use Presidio as an optional secondary pass
- Use AI as an optional second-pass explainer, not as the first-pass scanner

### Why this is the best balance

- Code heuristics let you catch code identifiers and architecture signals
- This makes the design easier to port to Java or other languages later
- Presidio is still useful when you want extra coverage for literal text
- AI can help summarize impact and explain edge cases, but using it for the first pass adds cost, variability, and operational complexity

### Suggested phased approach

1. Start with this scanner for scope discovery
2. Add a review workflow for false positives and false negatives
3. Optionally add AI later to generate migration narratives or estimate work packages

## Complexity and migration factors

Use these factors when estimating initial migration effort and ongoing support:

- Number of files containing PII references
- Number of distinct PII categories
- Number of back-end service files touching PII
- Number of data-access files with SQL or JDBC markers
- Number of front-end files that only display or transmit PII
- Number of outbound REST calls or custom transformation points
- Number of integration channels such as Kafka, MQ, or batch files
- Number of databases and schemas involved
- Whether encryption/protection happens centrally or in multiple services
- Whether JDBC driver substitution is technically feasible in each app
- Existing automated test coverage
- Volume of regression testing required
- Release coordination across teams
- Production support model and logging/observability changes
- Key rotation, tokenization format, and data re-identification requirements
- Performance sensitivity and latency tolerance
- Rollback strategy and dual-run validation requirements

### Complexity score definition

The scanner calculates complexity per file using a simple weighted heuristic. The current formula is:

```text
score =
  min(25.0, LOC / 40.0)
  + (PII matches x 2.5)
  + (code-change candidates x 3.0)
  + (REST calls x 1.5)
  + (SQL markers x 1.0)
  - (JDBC candidates x 1.5)
```

Additional adjustments:

- if the file is classified as front end, subtract `6`
- minimum final score is `1.0`
- the score is rounded to one decimal place

Complexity ratings are assigned as follows:

- `low`
  - score less than `12`
- `medium`
  - score greater than or equal to `12` and less than `24`
- `high`
  - score greater than or equal to `24`

What each factor is trying to represent:

- `LOC / 40`
  - larger files generally require more review and regression-test effort
- `PII matches x 2.5`
  - more sensitive-field references usually increase migration scope
- `code-change candidates x 3.0`
  - likely service or orchestration changes are the strongest complexity driver
- `REST calls x 1.5`
  - more outbound or orchestration activity usually increases implementation and testing effort
- `SQL markers x 1.0`
  - direct data-access patterns add review and migration complexity
- `JDBC candidates x 1.5`
  - likely JDBC-driver coverage reduces direct application-code change complexity
- front-end adjustment
  - front-end-only references often have lower direct CRDP migration impact than back-end and data-access files

Example:

If a file has:

- `LOC = 200`
- `10` PII matches
- `4` code-change candidates
- `2` REST calls
- `3` SQL markers
- `1` JDBC candidate

Then the score is:

```text
min(25, 200 / 40) = 5
PII impact = 10 x 2.5 = 25
Code-change impact = 4 x 3.0 = 12
REST impact = 2 x 1.5 = 3
SQL impact = 3 x 1.0 = 3
JDBC reduction = 1 x 1.5 = -1.5

Total = 46.5
Rating = high
```

Important note:

- This is a planning aid, not a precise engineering estimate.
- It is intended to rank likely migration and testing impact, not predict exact hours or staffing.

Customer-friendly explanation:

The complexity score is a directional indicator that helps compare files and applications by likely migration effort. In simple terms, complexity goes up when a file is larger, contains more sensitive-field references, and appears to require more back-end service or integration changes. Complexity goes down when the file looks like front-end-only code or when a JDBC-driver approach may reduce the amount of application code that needs to change. The score is best used to support scoping, sequencing, and testing discussions rather than as a direct estimate of calendar time or labor hours.

## Important limitations

- This is a static heuristic scanner, not a full semantic analyzer
- A file can reference PII without being the actual system-of-record touchpoint
- JDBC suitability is an estimate based on code markers, not a guarantee
- Customer-specific naming conventions may require extending the keyword rules

## Custom search patterns

Customers will often want to search for fields that are important to them but are not standard PII categories, such as:

- account number
- household id
- salary
- policy number
- loyalty id
- internal member id

For source-code scanning, the best approach is usually custom field-name aliases, not literal-value matching.

Why:

- Source code usually contains identifiers, DTO fields, SQL column names, JSON properties, and method arguments
- It usually does not contain many real account numbers, salaries, or household IDs as literal values
- Customers often have non-standard naming like `acctNbr`, `accntNbr`, `householdNbr`, or `hhId`

The scanner supports this with a JSON file passed using `--custom-patterns`.

Example file:

```json
{
  "custom_patterns": [
    {
      "name": "account-number",
      "category": "CUSTOM_ACCOUNT_NUMBER",
      "keywords": [
        "account_number",
        "account_num",
        "account_nbr",
        "acct_number",
        "acct_num",
        "acct_nbr",
        "accnt_nbr",
        "customer_account_number"
      ],
      "impact_hint": "Customer-defined account number field"
    },
    {
      "name": "household-id",
      "category": "CUSTOM_HOUSEHOLD_ID",
      "keywords": [
        "household_id",
        "household_identifier",
        "family_household_id",
        "household_nbr",
        "household_num",
        "hh_id",
        "hh_number"
      ],
      "impact_hint": "Customer-defined household identifier"
    },
    {
      "name": "salary",
      "category": "CUSTOM_SALARY",
      "keywords": ["salary", "annual_salary", "base_salary", "compensation_amount"],
      "impact_hint": "Customer-defined compensation field"
    }
  ],
  "custom_regex_patterns": [
    {
      "name": "household-id-literal",
      "category": "CUSTOM_HOUSEHOLD_ID_LITERAL",
      "pattern": "HH-[0-9]{5,10}",
      "impact_hint": "Literal household identifier format"
    },
    {
      "name": "account-number-literal",
      "category": "CUSTOM_ACCOUNT_NUMBER_LITERAL",
      "pattern": "\\b[0-9]{10,12}\\b",
      "impact_hint": "Literal account number format"
    },
    {
      "name": "salary-literal",
      "category": "CUSTOM_SALARY_LITERAL",
      "pattern": "\\$[0-9]{2,3},[0-9]{3}",
      "impact_hint": "Literal salary amount format"
    }
  ]
}
```

The scanner normalizes common code naming styles, so these aliases can match forms such as:

- `accountNumber`
- `acctNbr`
- `accntNbr`
- `householdId`
- `householdNbr`
- `hhId`

When a custom rule matches, the output will show:

- the matched attribute
- the custom category
- detector `custom_keyword`
- the custom pattern name

Regex rules are supported, but for source-code scanning they should usually be treated as optional and secondary.

Use regex only when customers specifically want to search for literal formats in code comments, test fixtures, config files, or sample payloads.

When a regex rule matches, the output will show detector `custom_regex`.

If you prefer not to see both the built-in and custom category for the same identifier, use `--custom-patterns-override-defaults`.

## How identifier matching works

The core scanner is designed for source code, not for discovering real sensitive values.

That means it looks primarily at:

- variable names
- DTO and model fields
- SQL column names
- JSON property names
- method parameters
- customer-specific aliases

### Example: `accntNbr`

If the scanner sees code like:

```java
String accntNbr;
```

it processes the identifier in these steps:

1. Extract the token from the source line
2. Normalize the identifier from camelCase/PascalCase into underscore form
3. Compare the normalized form against built-in and customer-defined aliases
4. Emit a match if an alias is found

For `accntNbr`, the flow is:

- raw token: `accntNbr`
- normalized token: `accnt_nbr`
- configured alias: `accnt_nbr`
- result: match

Example custom alias rule:

```json
{
  "name": "account-number",
  "category": "CUSTOM_ACCOUNT_NUMBER",
  "keywords": [
    "account_number",
    "account_num",
    "account_nbr",
    "acct_number",
    "acct_num",
    "acct_nbr",
    "accnt_nbr"
  ],
  "impact_hint": "Customer-defined account number field"
}
```

Because of normalization, one alias list can match multiple coding styles:

- `accntNbr` -> `accnt_nbr`
- `acctNbr` -> `acct_nbr`
- `householdId` -> `household_id`
- `hhId` -> `hh_id`
- `dateOfBirth` -> `date_of_birth`

This is the main reason the scanner works well for codebases with mixed naming conventions.

## Ownership analysis

The scanner now adds first-pass ownership fields without removing any existing metrics.

These fields help answer a key migration question:

- Is this file just referencing sensitive data?
- Or is this file a likely change owner?

Additional report fields include:

- `likely_change_owner`
- `ownership_confidence`
- `role_in_flow`
- `frontend_reference_only`
- `jdbc_substitution_candidate`
- `endpoint_correlation_score`
- `matched_endpoints`
- `matched_payload_fields`
- `likely_system_of_record_path`
- `related_files`

The report also includes a top-of-report DBA summary:

- likely JDBC table names detected in SQL statements
- sensitive columns associated with those tables
- number of files referencing each table

This is intended to make it easier to hand a focused table and column list to DBA teams before migration work begins.

The executive summary also includes:

- likely change owner counts
- role-in-flow counts
- complexity distribution
- top front-end to back-end correlations
- top back-end to data-access correlations
- likely JDBC tables and sensitive columns

Typical values for `likely_change_owner`:

- `frontend_reference_only`
- `backend_logic_owner`
- `data_access_owner`
- `jdbc_candidate`
- `supporting_model`
- `unknown`

Definitions:

- `frontend_reference_only`
  - File references sensitive fields but mostly looks like UI, client, proxy, or pass-through code.
  - Usually not the primary CRDP or JDBC implementation point.
- `backend_logic_owner`
  - File appears to own business logic, orchestration, transformation, or protection workflow.
  - Often the likely code-change location for CRDP REST integration.
- `data_access_owner`
  - File appears to own persistence, retrieval, or integration-layer handling of sensitive fields.
  - Common examples are repositories, DAOs, and storage-oriented handlers.
- `jdbc_candidate`
  - File looks like a data-access owner with strong JDBC or SQL evidence.
  - Candidate for lower-impact migration using a Thales JDBC driver approach.
- `supporting_model`
  - File looks like a DTO, request, response, record, or simple model class.
  - It contains field names but usually describes payload shape rather than the primary implementation point.
- `unknown`
  - Current heuristics do not provide enough evidence to identify the likely owner.

Typical values for `role_in_flow`:

- `display_only`
- `collects_and_sends`
- `receives_and_transforms`
- `persists_or_publishes`
- `protects_or_tokenizes`
- `supporting_model`
- `unknown`

Definitions:

- `display_only`
  - File mostly displays or binds sensitive data without strong evidence of sending or transforming it.
- `collects_and_sends`
  - File gathers sensitive fields and sends them to another tier or service.
- `receives_and_transforms`
  - File receives sensitive fields and performs business logic, mapping, or transformation.
- `persists_or_publishes`
  - File writes sensitive data to a database or publishes it to another system or channel.
- `protects_or_tokenizes`
  - File appears to directly call protection, tokenization, or encryption logic.
- `supporting_model`
  - File defines payload shape, DTO structure, or model fields rather than executing workflow logic.
- `unknown`
  - Flow role could not be determined from current heuristics.

Why `likely_change_owner` and `role_in_flow` can differ:

- `likely_change_owner` answers:
  - "Who probably needs to change?"
- `role_in_flow` answers:
  - "What does this file do in the sensitive-data path?"

Examples:

- `likely_change_owner=frontend_reference_only` with `role_in_flow=collects_and_sends`
  - A React or Node.js UI file references PII and sends it to the back end, but is not the likely primary change owner.
- `likely_change_owner=backend_logic_owner` with `role_in_flow=receives_and_transforms`
  - A service receives sensitive fields and performs business logic or CRDP orchestration.
- `likely_change_owner=jdbc_candidate` with `role_in_flow=persists_or_publishes`
  - A repository or SQL-heavy service persists sensitive fields and may be covered by a JDBC-driver approach.

Other ownership field meanings:

- `ownership_confidence`
  - Numeric confidence score for `likely_change_owner`, currently from `0.0` to `1.0`.
  - Higher means the heuristics found stronger evidence.
- `frontend_reference_only`
  - Boolean convenience flag.
  - `true` means the file is likely referencing or sending sensitive data rather than owning the implementation change.
- `jdbc_substitution_candidate`
  - Boolean convenience flag.
  - `true` means the file appears to be a plausible candidate for a JDBC-driver-based migration path.
- `endpoint_correlation_score`
  - Numeric score, currently from `0.0` to `1.0`.
  - Measures how strongly this file’s routes and payload fields correlate with related files.
- `matched_endpoints`
  - List of endpoints or route paths extracted from the file.
- `matched_payload_fields`
  - List of sensitive or business-relevant field names that overlap with the file’s payload or model structure.
- `likely_system_of_record_path`
  - List of database-style column or storage-path indicators associated with sensitive fields.
- `related_files`
  - List of file paths that appear correlated by route similarity, payload overlap, or data-access overlap.

Phase 2 also adds cross-file correlation:

- front-end API paths are compared with likely backend routes
- backend logic files are compared with likely data-access owners
- shared route tokens and shared payload fields increase ownership confidence

The ownership pass now also composes Spring class-level and method-level routes, so a controller such as:

- `@RequestMapping("/api/customers")`
- `@GetMapping("/{customerId}/profile")`

is treated as owning:

- `/api/customers/{customerId}/profile`

This makes front-end to back-end correlation much more useful for React, Angular, Node.js, and other clients that call REST endpoints.

Supporting model files are also handled more carefully. DTOs, records, request/response types, and simple model classes can still contain many sensitive field references, but they are now labeled as `supporting_model` when they look like payload-shape definitions rather than the real implementation point. That helps reduce false positives in:

- potential code-change candidates
- complexity scores
- ownership correlation

## Good next step

Run this against a few representative customer codebases and tune:

- keyword rules
- file classification markers
- complexity scoring
- exclusions for generated code and vendor folders
