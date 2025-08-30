***For any sections that do not apply, DO NOT delete them but rather explain WHY they are not relevant.***   

# \[Project Name\] \- Engineering Spec



# Overview

\[*Provide a 1-2 paragraph overview of the project and the problem we are trying to solve. If there is a product brief, rely on that for most of the justification. If there is not a product brief, include justification for the project here. Additionally, the definition of success and the product perspective needs to be approved by Product before the spec is filled out.*\] 


## Definition of Success

\[*Provide context on what success looks like for this project.*\] 

### Product Perspective

\[*Describe how the above definition will be measured / quantified from a product perspective.*\] 

### Engineering Perspective

\[*Describe how the above definition will be measured / quantified from an engineering perspective.*\] 

## Glossary / Acronyms

\[*Include any terms and acronyms that should be defined for reference.*\] 

## Requirements

### Functional Requirements

*\[Provide all functional requirements as agile stories “As a user I want to X in order to doY”\]*

### Non-Functional requirements

*\[Provide all non functional requirements such as scalability, tps, etc\]*

## Assumptions

*\[Provide any assumptions about the domain\]*

# Design

## Major Design Considerations

\[*This is the main section where major details will be documented. This may be a list of functionality, behaviors, interactions, etc. Call out major concepts and any considerations or details that a reviewer would not otherwise expect to see in a project like this. List steps in the process and main components.*\]

## Architecture Diagrams

\[*Add architectural diagrams, sequence diagrams, or any other drawings that help give a high-level overview of the new system or the components that are changing. For each diagram, provide a 1-2 sentence description of what the diagram shows.*\]

## API

\[*Identify new APIs or APIs whose behavior will be updated.*\]

| API | Description |
| :---- | :---- |
| **\[*ApiName*\] \[Method\] \[Path\]** | \[*Description of API, request/response structure, status codes*\] |

### Usage Estimates

\[What is the call pattern for each API? What is the *expected volume (RPM/RPS) that could inform the need for any load tests.*\]

## Events

\[*Identify new event flows or events that will be updated at a high-level (e.g. new infrastructure or sequence diagrams)*\]

## Front End Updates

\[*If your feature or project includes front end changes add mocks for how the user experience is being changed. Be sure to include before and after which clearly articulates how our customers will use this. For Metro, this likely refers to either the Agent Customer Admin tool, or Metro UI.* \]

## Data Storage

\[*Where is data stored? List any new databases or tables, and provide information on stored values in the table. Include indexes and constraints. Describe any special considerations about how the data will be read and written, including frequency, expected volume, whether data can be deleted, backup, and expiration. Can the data be manually inspected for debugging or investigative purposes? Are there any provisions for updating incorrect data?*\]

| Field | isRequired | Data Type | Description | Example |
| :---- | :---- | :---- | :---- | :---- |
| \[***FieldName***\] | \[*Yes|No*\] | \[*Dependent on technology*\] | \[*Description of data meaning.*\] | \[*Example value*\] |

## Auth

\[*Can this be accessed internally or externally? Are there limitations on who can access it? How will that be enforced?*\]

## Resiliency

\[*Describe how the product will react to diverse conditions. Ensure that we have designed for failure and can succeed in as many cases as possible. Consider using queues and/or notifications to eliminate failures and the impact of disruptions. Outline plans for failover, rollback, and retries.*\] 

## Dependencies

\[*List dependencies, either existing components or new required components that are outside the scope of this design. What use cases on each dependency are you using ? Action item : Verify these use cases work as expected.  For service dependencies, by sure to specify tasks for setting up network access (via Kong gateway or similar), requesting required access keys or scope permissions, etc\]*

## Dependents

\[*List components that will be dependent on the new features. These may be existing dependents that will be impacted by the changes, or future dependents that will be added after this project is complete. These are also called upstream dependencies*\]

# Observability

## Failure Scenarios

\[*List out different failure scenarios and how we plan to handle them, whether it’s propagating errors to downstream dependencies, or handling the error to provide an alternate successful path. List each dependency and how the product will attempt to be successful despite the dependency’s outage. If the product itself breaks, how can we still attempt to provide success to our users (through manual means or dependents’ reactions.* \]

## Logging

\[*What info, warn, and error logs will be collected? What information will we need to investigate errors or interesting scenarios? Does any data need to be sent to DataLake?*\]

## Metrics

\[*What events deserve metrics to help us understand usage or health? What thresholds will be set for those metrics? What dashboards or reports will allow viewing of the metrics?*\]

## Monitoring

\[*What provisions are in place for ensuring the features are behaving as expected? How will the team know if the features are not working properly? Describe any new or existing Panoptes Monitors, Zon tests. Splunk / Umbra Dashboard metrics to track (latency, requests, dependencies to monitor). Include access and error logging to be monitored*\]

# Testing

\[*Describe our approach to testing the features. Consider test automation (unit tests, integration tests, user acceptance tests), post deployment tests (pre-prod and/or prod), exploratory testing, static analysis tool, security analysis tool, and code coverage. Be explicit about test priority. Define the quality criteria the features must meet. Are there any designs that need to be considered to enable the testability of the features? What services will need to be mocked and what mocked data is required during development?\]* 

## Integration Tests

## Internal (Manual) Tests

## Performance/Load Tests

## End to End Test

## New technologies considered

*\[List new technologies considered, if you haven’t considered them please take a minute to explore how new technologies could help\]*

# Rollout Plan

\[*How will this feature be rolled out? Will it be turned on in stages? Do any components need to be rolled out in order? Are there any dependencies that need to be in place before this feature? How will we validate the release(s) or decide to rollback? 
## Pre Launch Checklist

## Launch Checklist

## Post Launch Checklist

## A/B Testing

\[*What existing A/B trials will impact this feature? Are any new A/B trials planned for experimentation or rollout? List the trials, treatments, and what they mean.*\]

| Trial | Treatment | Description |
| :---- | :---- | :---- |
| **\[*TrialName*\]** | CONTROL | \[*Expected behavior*\] |
|  | \[*TreatmentName*\] | \[*Expected behavior*\] |

# Release Milestones

\[*List the milestones that will be met during development of this project. Break the project down into as many milestones as feasible, including MVP (minimum viable product), to ensure that we are delivering incrementally. Include the approximate size of each milestone. Include future milestones that are not yet planned for delivery. You can use table to display a visual of the ticket dependenciesnbreakdown as well.*\] 

# Alternatives Considered

\[*List the alternatives that were considered when designing the implementation details for this project. What options did we rule out and why? Describing the alternatives will allow others to understand how we arrived at this design and not repeat evaluations of the same alternatives again. This section may also include original designs that needed to be pivoted away from during implementation. Please include a link to the Spike document so reviewers can look into the high-level alternatives considered if needed*\]

# Additional Sections for Modern Applications

## System Requirements (if applicable for desktop/mobile apps)
[*For desktop or mobile applications, specify minimum system requirements, supported OS versions, hardware requirements, and any special permissions needed.*]

## Installation & Distribution (if applicable)
[*How will the application be packaged and distributed? App stores, direct download, enterprise deployment? Include signing/notarization requirements.*]

## Performance Requirements
[*Define specific performance targets: response times, throughput, resource usage (CPU/memory), startup time, etc. Be quantitative where possible.*]

## Security & Privacy
[*Detail security measures, data encryption, authentication mechanisms, privacy policies, GDPR compliance, data retention policies, and any security audits planned.*]

## State Management
[*For complex applications, describe how application state will be managed, including state machines, data flow patterns, and synchronization strategies.*]

## Communication Protocols
[*If the system uses WebSockets, gRPC, or other communication protocols, define message formats, connection management, and error handling.*]

## Internationalization & Localization
[*Will the application support multiple languages? Define the i18n strategy, supported locales, and how translations will be managed.*]

## Accessibility
[*Define accessibility requirements: WCAG compliance level, screen reader support, keyboard navigation, color contrast requirements, etc.*]

## Offline Functionality (if applicable)
[*What features work offline? How is data synchronized? Conflict resolution strategies?*]

## Third-Party Integrations
[*List all external services, APIs, or libraries that will be integrated. Include version requirements and fallback strategies.*]

## Legal & Compliance
[*Any industry-specific compliance requirements (HIPAA, PCI-DSS, SOX)? Terms of service considerations? License requirements?*]

## Disaster Recovery & Backup
[*Define backup strategies, data recovery procedures, RTO/RPO targets, and disaster recovery plans.*]

## Cost Analysis
[*Estimated infrastructure costs, third-party service costs, licensing fees, and how costs scale with usage.*]

## Migration Strategy (if replacing existing system)
[*How will data be migrated? Parallel run strategy? Rollback procedures? User training requirements?*]

# Misc Considerations
[*Any other considerations specific to this project that don't fit in the above categories.*]