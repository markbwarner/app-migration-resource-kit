# Thales CRDP Maintenance And Support Estimating Guide

## Purpose

This guide is focused on **ongoing maintenance and support effort**, not the initial implementation effort, for a Thales CipherTrust REST Data Protection (CRDP) tokenization program.

It is intended to help frame support estimates for a large environment such as:

- approximately `250` applications
- multiple use cases including Kafka, WebSphere and Oracle, Azure Functions, Databricks, analytics, and general application integrations
- CRDP containers running in AKS
- batch data loads using Thales Batch Data Transformation (BDT)

This guide should be used as a planning framework, not as a fixed quote. The largest uncertainty drivers are:

- actual transactions per second
- number of clusters required
- application readiness and ownership maturity
- how many applications are actually onboarded in a given quarter

## Executive Summary

From a maintenance and support perspective, the effort is usually **much lower than the initial rollout effort**, but it is not trivial at this scale.

For a large multi-use-case estate, the ongoing support effort is usually driven by:

- number of active CRDP clusters
- production criticality and uptime expectations
- number of protected applications actually live at the same time
- policy and key lifecycle activity
- amount of application churn
- support maturity of the customer organization
- quality of documentation, runbooks, and technology transfer

At steady state, the support model is typically a combination of:

- platform and DevOps support for AKS and CRDP clusters
- application support for onboarding changes, break-fix, and regression support
- security and CipherTrust administration
- performance and capacity management
- DBA or data engineering support for batch and data lifecycle activities

For a large estate like this, a practical planning view is:

- **Low-complexity steady state**
  - `3` to `5` FTE equivalent across platform, application, and security support
- **Moderate-complexity steady state**
  - `5` to `8` FTE equivalent
- **High-complexity steady state**
  - `8` to `12+` FTE equivalent

These are blended support ranges and assume a production estate, not a temporary implementation surge.

## Key Questions To Ask The Customer

### Application Ownership And Readiness

- How many of the `250` applications are expected to be onboarded to CRDP in the first year versus later phases?
- For each application, who owns support after go-live?
- What percentage of the applications are supported by internal staff versus contractors or service providers?
- How much technology transfer exists for those applications?
- Which applications receive frequent changes and which are largely static?
- Which applications have complete runbooks, support contacts, and escalation paths?
- Which applications already have automated testing and release automation?

### Operational Criticality

- Which applications are business critical, revenue generating, regulatory critical, or customer facing?
- Which applications require `24x7` support?
- What are the uptime and recovery expectations?
- Which applications have tight batch windows or almost no downtime tolerance?
- Which workloads are latency sensitive?

### Integration And Architecture

- Which applications call CRDP directly versus through a shared wrapper or reusable library?
- Which applications only reference sensitive fields in the front end?
- Which applications are true back-end or data-access owners?
- How many applications perform protect operations, reveal operations, or both?
- Which integrations are synchronous APIs versus asynchronous Kafka, batch, or analytics use cases?
- Which applications can use a JDBC-style lower-impact approach instead of REST orchestration?

### Data And Batch Characteristics

- How many tables, files, or topics contain protected columns or fields?
- How many total columns are protected?
- What is the total data volume for initial loads and reprocessing?
- How often are batch loads, rekey, or re-encrypt operations expected?
- What batch windows are available for initial loads and for recurring maintenance?
- What is the average result set size for reveal-heavy use cases such as analytics?

### CipherTrust And Security Administration

- How many CRDP policies are expected?
- How many keys per policy?
- How many key rotations per year?
- How many non-key policy changes per year?
- How many CipherTrust Manager instances, HSM integrations, or geographic regions are involved?
- What separation of duty model is required?
- Who owns policy changes, approvals, and production rollout authority?

### AKS And Platform Operations

- How many AKS clusters are expected at steady state?
- Which workloads require separate clusters for isolation or scaling reasons?
- What observability stack is in place today?
- What are the standards for patching, vulnerability remediation, secrets, certificates, and backup?
- What autoscaling policies are planned?
- What network controls, private connectivity, and ingress patterns are required?

## Additional Factors To Consider

### Customer Readiness Metric

A customer readiness metric is one of the strongest predictors of support effort.

Suggested scoring dimensions:

- internal staffing depth
- percentage of contractor-owned applications
- amount of technology transfer completed
- quality of runbooks and documentation
- support process maturity
- test automation maturity
- release and incident management maturity

Suggested interpretation:

- **High readiness**
  - Strong internal ownership, good documentation, solid support process
  - Apply effort multiplier of `0.85x` to `1.0x`
- **Medium readiness**
  - Mixed ownership, partial documentation, moderate support maturity
  - Apply effort multiplier of `1.0x` to `1.2x`
- **Low readiness**
  - Thin staffing, high contractor dependence, poor technology transfer
  - Apply effort multiplier of `1.3x` to `1.7x`

### Application Portfolio Complexity

Support effort rises when the portfolio includes:

- multiple languages and frameworks
- a high number of unique integration patterns
- many teams with inconsistent standards
- uneven observability
- many reveal-heavy analytics use cases
- workloads that mix protect and reveal operations in the same transactions

### Change Velocity

Maintenance effort also depends on:

- number of releases per month
- policy changes per month
- onboarding of new applications
- key rotation frequency
- schema changes
- compliance-driven reconfiguration work

### Support Model

Support cost is materially affected by:

- business hours only versus `24x7`
- on-call expectations
- incident severity targets
- whether support is centralized or distributed
- whether one team owns both platform and application support

## Risk Reduction Recommendations

### General Recommendations

- Use **staff augmentation** when internal staffing is thin or the readiness metric is low.
- Establish **shared reusable security wrappers** or SDK-style integration helpers early.
- Standardize **golden integration patterns** for REST, Kafka, batch, and analytics use cases.
- Create **policy templates**, naming conventions, and a documented change-control model.
- Build **shared observability dashboards** for CRDP and AKS from the start.
- Require **runbooks** for protect, reveal, rollback, policy change, and cluster incident scenarios.
- Create a **support ownership matrix** by application, platform component, and data domain.
- Run **technology transfer sessions** before applications move to business-as-usual support.
- Use **dual-run or shadow validation** where feasible for higher-risk reveal or batch use cases.
- Maintain **common regression test packs** for reveal, protect, failure handling, and fallback behavior.

### Specific Recommendations For Low Readiness Customers

- assign dedicated support leads for the first production waves
- require contractor handoff documents and support transition checklists
- budget more support hours for incident diagnosis and application-specific troubleshooting
- prioritize onboarding reusable wrappers before large-scale rollout
- implement more aggressive staff augmentation and advisory support

## Example Support Profiles

The examples below combine:

- Application Code Sensitive Data Scanner complexity
- customer readiness
- data transformation considerations
- operational criticality
- integration mix

### Simple Application

Typical profile:

- scanner complexity: `Low`
- one back-end service
- one database or one simple API dependency
- one front end that mainly sends data
- `2` to `5` protected fields
- limited reveal use
- one policy
- low change velocity
- good documentation and stable internal ownership

Typical metrics:

- `1` front end
- `1` to `2` back-end services
- `1` data source
- `1` to `2` tables or topics
- `2` to `5` protected columns or fields
- result sets usually below `100` rows
- no hard real-time latency requirement

Steady-state support estimate:

- application support: `4` to `8` hours per month
- platform and security support allocation: `2` to `6` hours per month
- total blended support: `6` to `14` hours per month per application

### Medium Application

Typical profile:

- scanner complexity: `Medium`
- multiple services and one or two integration points
- both protect and reveal operations
- some batch or asynchronous processing
- moderate regression surface
- mixed internal and contractor ownership

Typical metrics:

- `1` to `2` front ends
- `2` to `5` back-end applications or services
- `2` to `4` databases, files, or topics
- `5` to `20` protected columns or fields
- `2` to `5` policies
- moderate transaction volume
- moderate reveal result set sizes

Steady-state support estimate:

- application support: `10` to `24` hours per month
- platform and security support allocation: `6` to `14` hours per month
- data and batch support allocation: `4` to `12` hours per month
- total blended support: `20` to `50` hours per month per application group

### Complex Application

Typical profile:

- scanner complexity: `High`
- multiple channels and integration patterns
- protect and reveal operations across several systems
- Kafka, batch, analytics, or mainframe adjacency
- high uptime sensitivity or limited batch windows
- large result sets or high data volume
- low customer readiness or weak support ownership

Typical metrics:

- `2+` front ends or client channels
- `5+` back-end services or applications
- `5+` integration points
- `20+` protected columns or fields
- multiple policies and more frequent policy changes
- large result sets such as analytics returning `5000` rows
- strong performance sensitivity

Steady-state support estimate:

- application support: `30` to `80` hours per month
- platform and security support allocation: `12` to `30` hours per month
- data and batch support allocation: `8` to `24` hours per month
- performance and incident analysis allocation: `8` to `20` hours per month
- total blended support: `58` to `154` hours per month per complex application group

## Applying The Model To The Provided Use Cases

### 1. Kafka Use Case

Profile:

- `5` Kafka topics
- `10` Java applications making calls
- producers and consumers both require changes

Support view:

- likely **complex**
- higher coordination cost because producers and consumers both matter
- support effort driven by message contract changes, replay handling, reveal/protect troubleshooting, and performance monitoring

### 2. Mainframe Transformation And WebSphere Use Cases

Profile:

- `3` WebSphere applications writing sensitive data to Oracle
- `10` Java applications making calls
- Azure Function invoking CRDP protect/reveal

Support view:

- likely **complex**
- higher operational risk due to older middleware patterns, Oracle dependency, and cross-platform troubleshooting
- additional support overhead for WebSphere release coordination and Azure Function integration

### 3. Databricks Use Cases

Profile:

- batch UDF transformation to Azure SQL DB
- `20` applications making calls to reveal sensitive data

Support view:

- likely **medium to complex**
- ongoing support depends on batch scheduling, data anomalies, reveal demand, and downstream SQL consumer expectations

### 4. Analytics Use Cases

Profile:

- `20` applications making reveal calls
- average result set size `5000` rows
- some Azure Functions

Support view:

- likely **complex**
- reveal-heavy workloads with larger result sets can create ongoing capacity and performance tuning requirements
- support effort will be strongly affected by query frequency and concurrency

### 5. Other `200` Applications

Support view:

- these should be segmented by scanner complexity and readiness, not treated as a single uniform block
- a practical triage model is:
  - `40%` simple
  - `40%` medium
  - `20%` complex

If the readiness metric is low, those percentages can shift upward toward medium and complex support effort.

### 6. Data Load Use Case

Profile:

- `150` million records
- BDT as primary load mechanism

Support view:

- initial load effort is implementation-heavy
- ongoing support depends on reruns, anomaly handling, rekey or re-encrypt operations, batch windows, schema drift, and rollback planning
- data support effort is especially sensitive to:
  - protected columns per row
  - downtime window
  - anomaly rate
  - reprocessing frequency

## Suggested Maintenance And Support Metrics

### Platform And Security Metrics

- number of active CRDP clusters
- number of CRDP policies
- number of keys
- key rotations per year
- non-key policy changes per year
- number of production incidents
- mean time to detect
- mean time to recover
- certificate and secret renewal events

### Application Metrics

- number of protected applications live
- number of application releases touching CRDP integrations
- number of front-end-only applications
- number of back-end logic owners
- number of data-access owners
- number of JDBC candidates
- number of supporting DTO/model changes that trigger downstream testing

### Data Metrics

- total protected tables and views
- total protected columns
- total rows processed
- total terabytes processed
- number of batch reruns
- number of anomaly exceptions
- rekey and re-encrypt events per year

## AKS DevOps Support Tasks And Activities

### Cluster Lifecycle

- cluster provisioning and decommissioning
- AKS version upgrades
- node pool design and lifecycle
- patching and image refresh
- backup and restore validation

### Scaling And Capacity

- HPA and VPA tuning if used
- cluster autoscaler tuning
- node pool sizing
- quota and limit management
- capacity forecasting

### Security And Configuration

- secrets management
- certificate management
- network policies
- ingress and private connectivity
- identity and RBAC reviews
- vulnerability scanning and remediation

### Reliability And Operations

- health probes and pod disruption budgeting
- failover testing
- DR and recovery rehearsal
- namespace standards
- log routing and retention
- alert tuning

### Deployment And Release Support

- release windows and change coordination
- rollback procedure validation
- environment promotion controls
- configuration drift detection

## Performance Monitoring Metrics

### CRDP Metrics To Track

- `protect_success_count`
- `protect_failure_count`
- `protect_bulk_success_count`
- `protect_bulk_failure_count`
- `protect_bulk_success_transaction_count`
- `protect_bulk_failure_transaction_count`
- `reveal_success_count`
- `reveal_failure_count`
- `reveal_bulk_success_count`
- `reveal_bulk_failure_count`
- `reveal_bulk_success_transaction_count`
- `reveal_bulk_failure_transaction_count`
- `unique_ip_address_count`

### Useful Derived Metrics

- protect success rate
- reveal success rate
- bulk success rate
- average transactions per bulk request
- reveal-to-protect ratio
- unique caller growth trend
- failure spikes by workload type

### Kubernetes And AKS Metrics To Pair With CRDP Metrics

- CPU utilization by pod and node
- memory utilization by pod and node
- pod restart count
- replica count over time
- request latency and p95/p99 latency
- network errors and timeouts
- node pressure events
- autoscaling frequency

## When To Use A Separate Kubernetes Cluster

More clusters usually do mean more support cost. Additional clusters increase:

- patching effort
- upgrade coordination
- observability overhead
- certificate and secret management
- RBAC and network administration
- troubleshooting complexity

You should usually split clusters only when there is a strong reason.

### Good Reasons For Separate Clusters

- strong blast-radius isolation is needed
- materially different scaling patterns
- different uptime or change windows
- different regulatory or tenant boundaries
- different network segmentation or access models
- different operational ownership teams
- high-volume analytics or batch workloads would create noisy-neighbor risk

### Good Reasons To Keep Workloads Together

- similar latency and scaling profiles
- same operational ownership
- similar patching and release cadence
- low need for tenant or regulatory isolation
- limited support staff

### Practical Initial Design Approach

Until TPS is known, a reasonable starting pattern is:

- separate production from non-production
- consider separate workload classes rather than one cluster per application
- use namespaces and node pools before creating many clusters

A practical early grouping could be:

- interactive API and application workloads
- Kafka and event-driven workloads
- batch and Databricks-adjacent transformation workloads
- analytics and large reveal workloads
- high-isolation workloads if required by policy or organizational boundaries

## Role-Based Activities And Monthly Support Estimates

These are **steady-state monthly support ranges** for the running environment, assuming production support after the initial rollout wave.

### DevOps Or SRE

Activities:

- AKS operations
- patching and upgrades
- autoscaling and node pool tuning
- cluster incidents
- observability and alert maintenance
- certificate, secret, and network operations

Estimated monthly effort:

- base for first `2` clusters: `80` to `140` hours per month
- add `20` to `35` hours per month for each additional cluster

For `5` clusters, a practical range is:

- `140` to `245` hours per month

### CipherTrust Platform And Security Administration

Activities:

- policy administration
- key lifecycle operations
- key rotation planning and execution support
- access control and separation-of-duty support
- audit support
- production change review

Estimated monthly effort:

- `40` to `100` hours per month

### Application Support And Integration Engineering

Activities:

- break-fix support for application integrations
- wrapper or shared library maintenance
- support for release cycles touching protected flows
- troubleshooting reveal and protect failures
- coordination with application owners and vendors

Estimated monthly effort:

- simple active applications: `4` to `8` hours each per month
- medium active applications: `10` to `24` hours each per month
- complex active applications: `30` to `80` hours each per month

For planning at portfolio level, group applications by complexity rather than multiplying `250` by one flat number.

### DBA Or Data Engineering Support

Activities:

- BDT planning and reruns
- data anomaly resolution
- schema-change coordination
- SQL performance review
- rekey and re-encrypt support

Estimated monthly effort:

- `40` to `120` hours per month

### Performance And Capacity Engineering

Activities:

- analyze CRDP success and failure patterns
- tune autoscaling thresholds
- review reveal-heavy and analytics-heavy workloads
- support capacity planning
- validate cluster split or consolidation decisions

Estimated monthly effort:

- `20` to `60` hours per month

### Service Management, Release, And On-Call Coordination

Activities:

- incident management
- release scheduling
- change advisory coordination
- major incident review
- support reporting and SLA tracking

Estimated monthly effort:

- `20` to `60` hours per month

## Suggested Estimating Method

For each application or application group, calculate:

`Support Effort = Base Complexity x Readiness Multiplier x Criticality Multiplier x Data/Performance Multiplier`

Suggested qualitative multipliers:

- readiness
  - high: `0.85x` to `1.0x`
  - medium: `1.0x` to `1.2x`
  - low: `1.3x` to `1.7x`
- criticality
  - normal business hours: `1.0x`
  - near `24x7`: `1.2x` to `1.4x`
  - highly critical: `1.4x` to `1.8x`
- data and performance sensitivity
  - low: `1.0x`
  - moderate: `1.1x` to `1.3x`
  - high: `1.3x` to `1.6x`

## Final Guidance

For the environment described, the maintenance and support estimate should be presented as:

- a **range**, not a point estimate
- segmented by **simple, medium, and complex application groups**
- adjusted by **customer readiness**
- adjusted again when **actual TPS, cluster count, and onboarding waves** are known

The best practical next step is:

1. Segment the `250` applications by scanner complexity and likely change owner.
2. Score each major application group with a readiness metric.
3. Group workloads into a preliminary AKS cluster design.
4. Convert those groups into monthly support ranges by role.
5. Re-baseline once real CRDP load metrics are available.
