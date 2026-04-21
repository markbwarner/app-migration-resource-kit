# Thales CRDP Maintenance And Support Executive Summary

## Purpose

This document provides a customer-facing summary of the ongoing maintenance and support considerations for a Thales CipherTrust REST Data Protection (CRDP) tokenization program. It is intended to support planning conversations, not replace a detailed implementation or operations estimate.

## Start With Scope Validation

Before estimating support effort, customers should validate the true scope of the program by running the **Application Code Sensitive Data Scanner Assessment Tool**.

In many modern multi-tier environments:

- front-end applications reference sensitive fields
- back-end services own business logic and API endpoints
- database, batch, Kafka, analytics, and integration layers perform the actual protection or reveal path

That means a customer may initially believe `250` applications are in scope, but the assessment may show that only a much smaller number of back-end or data-access applications are the true change owners. This can significantly reduce both implementation effort and long-term support effort.

## What Usually Drives Ongoing Support

Once applications are onboarded, ongoing effort is usually driven less by application code changes and more by shared operational concerns such as:

- AKS and Kubernetes platform support
- CipherTrust policy and access administration
- monitoring and alert review
- capacity and performance management
- data and batch support
- production release and incident coordination

In many cases, the ongoing additional application-developer effort is low after rollout because most changes to tokenization policy, key rotation, access behavior, and masking behavior are handled in CipherTrust Manager rather than through repeated application code changes.

## Roles Commonly Involved

Even though the incremental effort per application can be modest, the operating model may involve several roles across the organization.

Typical roles include:

- application developers and integration engineers
- DBAs and data engineering teams
- cloud architects
- DevOps or SRE teams supporting AKS and Kubernetes
- Thales security administrators
- performance and capacity engineers
- Databricks or analytics specialists
- service-management and release-coordination teams
- customer application owners and support leads

## Planning View By Steady-State Complexity

For customer planning purposes, a practical blended FTE view is:

- **Low-complexity steady state**
  - `3` to `5` FTE equivalent across platform, application, database, and security-related support roles
- **Moderate-complexity steady state**
  - `5` to `8` FTE equivalent across those same roles
- **High-complexity steady state**
  - `7` to `10+` FTE equivalent across those same roles

These ranges assume a production estate and should be adjusted once the customer confirms the actual number of in-scope applications, transaction volume, cluster design, and operational ownership model.

## Example Incremental Support Profiles

These examples describe the additional monthly support effort associated with tokenization capability, not the full support cost of the application itself.

### Simple Application

Typical characteristics:

- low scanner complexity
- one back-end service
- limited reveal usage
- good documentation and stable ownership

Typical incremental support:

- about `1` additional application-support hour per month if any
- about `1` to `3` hours per month of shared platform and security allocation
- about `2` to `4` total blended incremental hours per month per application

### Medium Application

Typical characteristics:

- medium scanner complexity
- multiple services or integration points
- both protect and reveal operations
- some batch or asynchronous processing

Typical incremental support:

- about `2` additional application-support hours per month
- about `3` to `6` hours per month of shared platform and security allocation
- about `2` to `4` hours per month of data and batch allocation
- about `7` to `12` total blended incremental hours per month per application group

### Complex Application

Typical characteristics:

- high scanner complexity
- multiple channels or integration patterns
- Kafka, analytics, batch, or legacy-platform adjacency
- stronger uptime or performance sensitivity

Typical incremental support:

- about `4` additional application-support hours per month
- about `6` to `10` hours per month of shared platform and security allocation
- about `4` to `8` hours per month of data and batch allocation
- about `4` to `8` hours per month of performance and incident analysis allocation
- about `18` to `30` total blended incremental hours per month per complex application group

## Factors That Most Affect Level Of Effort

The most important planning factors are usually:

- rollout pace by quarter
- customer readiness and technology transfer
- percentage of applications with complete runbooks and support ownership
- number of true back-end and data-access owners after assessment
- number of AKS clusters needed at steady state
- number of CRDP policies, keys, and policy changes
- number of reveal-heavy analytics and batch workloads
- uptime, latency, and batch-window sensitivity

## Cluster Design And TPS Matter

The number of AKS clusters is one of the strongest drivers of ongoing support cost. More clusters usually increase:

- patching effort
- upgrade coordination
- observability overhead
- certificate and secret management
- RBAC and network administration
- troubleshooting complexity

That is why final cluster design should remain provisional until transaction-per-second requirements, workload mix, and scaling behavior are better understood.

### Practical Starting Approach

- separate production from non-production
- consider separate workload classes rather than one cluster per application
- use namespaces and node pools before creating many clusters
- create separate clusters only when there is a strong reason

### Common Reasons To Split Clusters

- blast-radius isolation is needed
- materially different scaling patterns
- different uptime or change windows
- regulatory or tenant boundaries
- network segmentation or access isolation requirements
- noisy-neighbor risk from analytics or batch workloads

## How To Reduce Risk

Good practices that usually reduce both rollout risk and long-term support effort include:

- run the assessment tool early to narrow true scope
- use shared wrappers and reusable integration patterns
- standardize policy templates and operational naming conventions
- automate monitoring with Prometheus and dashboarding
- tune alerting to avoid unnecessary operational noise
- complete technology transfer before support transitions
- use staff augmentation where readiness is low or staffing is thin
- group workloads into sensible AKS workload classes rather than creating unnecessary clusters

## Recommended Next Step

For customer planning, a practical next step is:

1. Run the assessment tool to validate the true in-scope back-end and data-access population.
2. Segment applications into simple, medium, and complex support groups.
3. Confirm readiness, ownership, and operational documentation quality.
4. Define a preliminary AKS workload grouping.
5. Convert the validated scope into support ranges by role.

## Final Message

The most important message for customers is that ongoing support for CRDP tokenization is often materially lower than the initial rollout effort, especially when:

- the assessment tool narrows the true change-owner population
- reusable integration patterns are used
- CipherTrust policy administration is centralized
- monitoring and operational support are standardized

That is why scope validation and operating-model design are so important before committing to a long-term support estimate.
