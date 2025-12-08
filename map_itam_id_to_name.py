reviews per your notes?
Are PSRM approvals documented?
Who are PSRM team members and what is their authority?
Is PSRM approval aligned with IAM-440(c) requirement for authorization by Information System Owner or Technology Infrastructure Owner?
Review privileged ID validation per IAM-440(c):
For sampled privileged accounts, verify review validated:
Account still required for business purpose
Account owner per IAM-014 is current and appropriate
Authorized staff per IAM-440(c) who can access account are documented
Access is restricted to authorized staff per IAM-440(c)
Account complies with IAM-440 vaulting and control requirements
Examine findings and remediation:
Were any privileged IDs found non-compliant or unauthorized?
What remediation actions were taken?
Were unauthorized privileged IDs removed or restricted per IAM-440(c)?
Follow-up on remediation completion
Test governance effectiveness:
Did reviews identify any unvested privileged accounts per IAM-440(a)?
Were privileged accounts without owners per IAM-014 identified?
Did reviews catch privileged accounts lacking proper authorization per IAM-440(c)?
Review integration with other processes per IAM-440:
Are PID team findings escalated appropriately?
Do findings result in provisioning or deprovisioning actions per IAM-440?
Are findings tracked to closure?
Verify documentation and record retention:
Are monthly review reports retained per compliance requirements?
Can historical reviews be retrieved for audit purposes?
Is there trend analysis of privileged ID population and compliance?
Expected Evidence: PID team monthly workflow procedures per your notes; completed monthly review reports for sample period with PSRM approvals; evidence of monthly cadence; review scope documentation covering all privileged IDs per IAM-440; PSRM team authorization documentation; privileged ID validation records per IAM-440(c); findings and remediation tracking; governance metrics and trends; document retention evidence.
Pass Criteria: Monthly PID team workflow per your notes is documented and operational; reviews conducted every month without gaps; PSRM team approvals obtained per your notes; review scope covers all privileged IDs per IAM-440; privileged ID validation per IAM-440(c) includes account necessity, ownership per IAM-014, and authorized staff; findings are identified and remediated; governance is effective in ensuring IAM-440 compliance; documentation is retained.
Potential Findings: PID team monthly workflow per your notes not formalized or documented; reviews not conducted monthly with gaps in cadence; PSRM approvals per your notes missing or incomplete; review scope incomplete (missing service accounts, break-glass accounts per IAM-570/571); privileged ID validation per IAM-440(c) inadequate; findings not remediated; unvested privileged accounts per IAM-440(a) not identified by reviews; accounts without owners per IAM-014 not detected; unauthorized access per IAM-440(c) not caught; documentation not retained.
Data Analytics (DA) Test Procedures:
DA Test 1: Privileged Credential Vaulting Gap Analysis
Objective: Identify all privileged accounts not vaulted per IAM-440(a) through comprehensive data analysis.
Data Required:
Complete database user account population across all five products
Privileged attribute designation per IAM-440 for each account
OneVault credential inventory
HashiCorp secret inventory
Account ownership per IAM-014
Analytics Steps:
Extract complete database account population: Username, Account Type, Database Product, Instance, Environment, Privileged Attribute per IAM-440, Account Owner per IAM-014, Creation Date, Status.
Flag all accounts with privileged attribute per IAM-440: DBA roles, SUPERUSER, administrative privileges, accounts with GRANT capability, accounts with CREATE/DROP USER privileges.
Extract OneVault inventory: Vaulted Account Names, Database System, Vault Entry Date.
Extract HashiCorp inventory: Vaulted Service Account Names, Associated Application, Database System.
Perform left join: Database Privileged Accounts LEFT JOIN (OneVault UNION HashiCorp) ON Account Name to identify accounts with privileged attributes per IAM-440 not in either vault.
Generate unvested privileged account report showing:
Account username
Database product and instance
Privileged attribute type per IAM-440
Account owner per IAM-014 (or flag if no owner)
Account creation date (age of unvested account)
Environment (production vs. non-production)
Calculate vaulting gap metrics:
Total privileged accounts per IAM-440: [count]
Vaulted in OneVault or HashiCorp: [count] ([percentage]%)
NOT vaulted: [count] ([percentage]%)
Vaulting gap by database product (are some products worse than others?)
Vaulting gap by environment (production vs. non-production)
Vaulting gap by account type (DBA, service, break-glass per IAM-570/571)
Analyze unvested account patterns:
Are unvested accounts concentrated in specific databases or teams?
Account age distribution (recently created vs. long-standing gaps)
Ownership patterns (unvested accounts often lack owners per IAM-014?)
Risk-rank unvested accounts:
High risk: Production DBA accounts, SUPERUSER privileges, break-glass per IAM-570/571
Medium risk: Production service accounts, administrative roles
Lower risk: Non-production privileged accounts (still must comply with IAM-440(a))
Cross-reference against exception documentation per IAM-007:
Are any unvested accounts documented exceptions?
Exceptions with compensating controls vs. unjustified gaps
Generate remediation priority list based on risk ranking and compliance with IAM-440(a).
Expected Output: Unvested privileged account report violating IAM-440(a); vaulting coverage metrics by database product, environment, and account type; pattern analysis of vaulting gaps; risk-ranked remediation list; exception validation against IAM-007; trend analysis if historical data available.
Potential Findings: Significant percentage of privileged accounts per IAM-440 not vaulted violating IAM-440(a); production DBA accounts without vaulting; service accounts with hardcoded credentials violating IAM-470(e); break-glass accounts per IAM-570/571 not in OneVault; vaulting gaps concentrated in specific database products or teams; unvested accounts lack ownership per IAM-014; no exceptions documented per IAM-007 for unvested privileged accounts; long-standing vaulting gaps indicating systemic non-compliance with IAM-440.
DA Test 2: OneVault Alert and Ticket Reference Compliance Analysis
Objective: Analyze OneVault credential withdrawals to verify alert generation per IAM-440(e) and ticket/CR reference compliance.
Data Required:
OneVault withdrawal log for review period (3-6 months)
OneVault alert log for same period
Change Request or technology ticket system data
Analytics Steps:
Extract OneVault withdrawal data: Withdrawal ID, Timestamp, Username (Bank ID per IAM-014), Privileged Account Accessed, Database System, Ticket/CR Reference per IAM-440(e), Session Duration.
Extract OneVault alert data: Alert ID, Alert Timestamp, Withdrawal ID, Alert Recipients, Alert Delivery Status.
Calculate total credential withdrawals: [count] during review period.
Analyze alert generation per IAM-440(e):
Join withdrawals with alerts ON Withdrawal ID
Identify withdrawals without corresponding alerts violating IAM-440(e)
Calculate alert generation rate: (Withdrawals with Alerts / Total Withdrawals) * 100%
Target: 100% per IAM-440(e) requirement
Analyze ticket/CR reference compliance per IAM-440(e):
Count withdrawals with ticket/CR reference populated
Count withdrawals with null or empty ticket reference violating IAM-440(e)
Calculate ticket reference compliance rate: (Withdrawals with Ticket / Total Withdrawals) * 100%
Target: 100% per IAM-440(e) pre or post authorization requirement
Validate ticket references per IAM-440(e):
For sample of withdrawal records, query ticket system with provided reference
Verify ticket exists and corresponds with valid technology request per IAM-440(e)
Calculate valid ticket reference rate
Analyze alert delivery:
Alerts successfully delivered to designated recipients (Harish per your notes)
Failed alert deliveries
Alert delivery timeliness (real-time vs. delayed)
Identify high-risk patterns:
Users with frequent credential withdrawals without tickets violating IAM-440(e)
Database systems with low ticket reference compliance
Time periods with alert generation failures
Analyze withdrawal patterns:
Total withdrawals per user (identify heavy privileged access users)
Total withdrawals per privileged account
Withdrawals by time of day (off-hours access warrants extra scrutiny)
Withdrawals by database environment (production vs. non-production)
Generate compliance metrics:
Alert generation compliance per IAM-440(e): [percentage]%
Ticket reference compliance per IAM-440(e): [percentage]%
Valid ticket reference rate
Alert delivery success rate
Create exception reports:
List of withdrawals without alerts per IAM-440(e)
List of withdrawals without ticket references per IAM-440(e)
List of withdrawals with invalid ticket references
Users with pattern of non-compliance
Expected Output: OneVault withdrawal and alert analysis report; alert generation compliance metrics per IAM-440(e); ticket/CR reference compliance per IAM-440(e); ticket validation results; alert delivery metrics; high-risk pattern identification; user and system compliance breakdown; exception reports requiring investigation.
Potential Findings: Credential withdrawals without alerts violating IAM-440(e); alert generation rate below 100% per IAM-440(e); withdrawals without ticket/CR references violating IAM-440(e); invalid or non-existent ticket references violating pre/post authorization per IAM-440(e); alert delivery failures to designated recipients; specific users or systems with low compliance with IAM-440(e); pattern of off-hours access without proper authorization per IAM-440(e).
DA Test 3: Password Rotation Compliance Analysis
Objective: Analyze password rotation compliance for interactive privileged accounts per IAM-440(b) and service accounts.
Data Required:
OneVault usage history (credential withdrawals)
OneVault password change history
HashiCorp service account rotation log
Service account rotation schedules
Analytics Steps:
Extract OneVault privileged account usage: Account Name, Session Start Timestamp, Session End Timestamp, Username per IAM-014.
Extract OneVault password change events: Account Name, Password Change Timestamp, Change Method (automated vs. manual).
Analyze interactive account rotation per IAM-440(b):
For each privileged session, calculate time between session end and next password change
Identify sessions NOT followed by password change violating IAM-440(b)
Calculate rotation compliance rate: (Sessions with Post-Session Rotation / Total Sessions) * 100%
Target: 100% per IAM-440(b) requirement
Measure rotation timeliness per IAM-440(b):
Average time lag between session end and password rotation
Should be immediate or near-immediate per IAM-440(b)
Identify delayed rotations exceeding acceptable threshold (e.g., >1 hour)
Extract HashiCorp service account data: Account Name, Last Rotation Date, Rotation Schedule (e.g., 90 days per your notes), Application.
Calculate service account rotation compliance:
Days since last rotation for each service account
Compare against rotation schedule
Identify overdue service accounts: Days Since Last Rotation > Rotation Schedule
Calculate compliance rate: (Accounts Rotated on Schedule / Total Service Accounts) * 100%
Analyze rotation failures:
Query system logs for failed rotation attempts
Count and categorize rotation failures by type
Measure time to remediate failed rotations
Break down compliance by dimensions:
Rotation compliance by database product
Rotation compliance by environment (production vs. non-production)
Rotation compliance by account type (DBA vs. service vs. break-glass per IAM-570/571)
Identify high-risk non-compliance:
Production DBA accounts not rotated per IAM-440(b)
Service accounts significantly overdue for rotation (e.g., >180 days)
Accounts with passwords never rotated since creation
Generate rotation compliance trends:
If historical data available, show compliance improvement or degradation over time
Identify periods with rotation issues
Calculate metrics:
Interactive account rotation compliance per IAM-440(b): [percentage]%
Service account rotation compliance: [percentage]%
Average rotation lag time for interactive accounts
Average days overdue for non-compliant service accounts
Expected Output: Interactive privileged account rotation compliance report per IAM-440(b); service account rotation compliance report; rotation timeliness analysis; overdue account listing; rotation failure analysis; compliance breakdown by database product, environment, and account type; trend analysis; high-risk non-compliance identification.
Potential Findings: Interactive privileged sessions not followed by password rotation violating IAM-440(b); rotation compliance rate below 100% per IAM-440(b); delayed rotations not immediate after sessions per IAM-440(b); service accounts significantly overdue for rotation; rotation failures not remediated timely; specific database products or environments with low rotation compliance; accounts with passwords never rotated since creation violating IAM-440(b); manual rotation required instead of automated per IAM-440(b).
DA Test 4: Generic and Break-Glass Privileged Account Analysis
Objective: Analyze generic accounts per IAM-250/251 and break-glass accounts per IAM-570/571 with privileged attributes to verify IAM-440 compliance.
Data Required:
Complete account inventory with account type classification
Privileged attribute designation per IAM-440
Account ownership per IAM-014
OneVault vaulting status
Usage logs showing individual staff attribution
Analytics Steps:
Extract generic account population per IAM-250/251: Account Name, Database Product, Environment, Privileged Attribute per IAM-440, Account Owner per IAM-014.
Filter to generic accounts WITH privileged attributes per IAM-440 (these must comply with all IAM-440 requirements).
Analyze generic privileged account compliance:
Count total generic privileged accounts
Identify generic privileged accounts WITHOUT owner per IAM-014 (violates IAM-014 and IAM-440(c))
Identify generic privileged accounts NOT vaulted (violates IAM-440(a))
Extract break-glass account inventory per IAM-570/571: Account Name, Database Product, Break-Glass Designation, Privileged Attribute per IAM-440, Vaulted in OneVault (per your notes).
Analyze break-glass account compliance per IAM-570/571 and IAM-440:
Count total break-glass accounts per IAM-570/571
Verify all break-glass accounts are in OneVault per your notes
Identify break-glass accounts missing from OneVault (violates IAM-440(a) and your process notes)
Extract usage logs for generic privileged accounts:
Account Name, Access Timestamp, Session Details
Analyze attribution per IAM-440(d) and IAM-251(d):
For generic privileged account usage, can specific staff member be identified?
Check for ticket/CR references per IAM-440(e) associating usage with individual
Verify audit logs per IAM-440(d) provide full auditing and non-repudiation per IAM-251(d)
Identify high-risk generic privileged accounts:
Production generic DBA accounts (highest risk if attribution fails per IAM-440(d))
Generic accounts with multiple authorized users (higher risk of misuse)
Generic privileged accounts without recent access reviews
Analyze break-glass usage patterns per IAM-570/571:
Frequency of break-glass account usage
Break-glass accounts used routinely vs. only for emergencies (should be emergency-only per IAM-570)
Break-glass usage with proper authorization and compensating controls per IAM-570
Cross-reference against authorization documentation per IAM-440(c):
Do generic privileged accounts have documented authorized staff lists per IAM-440(c)?
Is authorization approved by Information System Owner or Technology Infrastructure Owner per IAM-440(c)?
Generate compliance metrics:
Generic privileged accounts with owners per IAM-014: [percentage]%
Generic privileged accounts vaulted per IAM-440(a): [percentage]%
Generic privileged accounts with attribution per IAM-440(d) and IAM-251(d): [percentage]%
Break-glass accounts in OneVault per IAM-440(a) and your notes: [percentage]%
Expected Output: Generic privileged account inventory per IAM-250/251 with compliance status; break-glass account inventory per IAM-570/571 with vaulting status; ownership analysis per IAM-014; vaulting gap identification per IAM-440(a); attribution validation per IAM-440(d) and IAM-251(d); break-glass usage pattern analysis per IAM-570/571; authorization documentation review per IAM-440(c); compliance metrics; high-risk account identification.
Potential Findings: Generic accounts with privileged attributes per IAM-440 lacking owners violating IAM-014 and IAM-440(c); generic privileged accounts not vaulted violating IAM-440(a); cannot identify which staff used generic privileged account violating IAM-440(d) and IAM-251(d); break-glass accounts per IAM-570/571 not in OneVault violating IAM-440(a) and your process notes; break-glass accounts used routinely instead of emergencies only violating IAM-570; generic privileged accounts lack authorized staff documentation per IAM-440(c); inadequate attribution mechanisms per IAM-251(c) and IAM-440(d) for generic account usage.
DA Test 5: Service Account Credential Storage Pattern Analysis
Objective: Analyze service account population to identify hardcoded credentials violating IAM-470(e) and non-vaulted accounts violating IAM-440(a).
Data Required:
Complete service account inventory
HashiCorp vault inventory
Application deployment artifacts and configurations (if accessible)
Database connection source analysis
Analytics Steps:
Extract service account population: Account Name, Associated Application, Database Product, Environment, Privileged Attribute per IAM-440, Account Owner per IAM-014.
Extract HashiCorp vaulted service accounts: Account Name, Application, Vault Entry Date.
Identify service accounts NOT in HashiCorp:
Left join service accounts to HashiCorp inventory
Flag service accounts without vault entry (potential hardcoded credentials violating IAM-470(e) and IAM-440(a))
Analyze vaulting coverage for service accounts:
Total service accounts: [count]
Vaulted in HashiCorp: [count] ([percentage]%)
NOT vaulted: [count] ([percentage]%)
Target: 100% per IAM-440(a) for service accounts with privileged attributes, best practice for all
Risk-rank unvested service accounts:
Production service accounts with privileged attributes (highest risk per IAM-440)
Production service accounts without privileged attributes (high risk per IAM-470(e))
Non-production service accounts (medium risk)
If application deployment artifacts accessible, analyze for hardcoded credentials:
Scan configuration files for connection strings with embedded passwords
Search for password variables with literal values
Identify credential patterns suggesting hardcoding per IAM-470(e)
Cross-reference findings with unvested service account list
Analyze database connection sources:
Query database logs for service account connection sources
Identify connection source IPs or hostnames
Determine if connections come from application servers (expected) or other sources (suspicious)
Flag service accounts with connections from unexpected sources (possible hardcoded credential sharing)
Analyze service account ownership per IAM-014:
Service accounts without assigned owners (violates IAM-014)
Owners no longer with organization (orphaned accounts)
Single owner with excessive number of service accounts
Correlate unvested service accounts with PID team reviews:
Were unvested service accounts identified in monthly PID reviews per your notes?
If not, indicates PID review scope may not include service accounts adequately
Generate compliance metrics:
Service account HashiCorp vaulting rate: [percentage]%
Service accounts with privileged attributes vaulted per IAM-440(a): [percentage]%
Service accounts with owners per IAM-014: [percentage]%
Suspected hardcoded credential rate (based on analysis): [percentage]%
Expected Output: Service account vaulting gap analysis; unvested service account report violating IAM-440(a); risk-ranked list of non-vaulted accounts; hardcoded credential detection results per IAM-470(e); ownership analysis per IAM-014; connection source analysis; PID review effectiveness for service accounts; compliance metrics; remediation priority list.
Potential Findings: Significant percentage of service accounts not vaulted in HashiCorp violating IAM-440(a); service accounts with privileged attributes per IAM-440 lacking vaulting; suspected hardcoded credentials in applications violating IAM-470(e); service accounts connecting from unexpected sources suggesting credential sharing; service accounts without owners violating IAM-014; PID team monthly reviews per your notes not covering service accounts adequately; orphaned service accounts no longer needed; production service accounts with hardcoded credentials representing critical risk per IAM-470(e) and IAM-440(a).
RISK 3: UNAUTHORIZED DATABASE ACCESS - USERS OBTAINING OR RETAINING ACCESS WITHOUT PROPER AUTHORIZATION
Risk Title:
Unauthorized Database Access - Users Obtaining or Retaining Access Without Proper Authorization
Risk Description:
Users may obtain or retain database access without proper authorization through multiple failure points in the access lifecycle, violating fundamental IAM principles that access must be formally approved before granting per IAM-440 and that only authorized users with valid business rationale can access Group Information and Technology Assets. This risk manifests when access is provisioned without required approvals from People Leader, Information System Owner, or Technology Infrastructure Owner per IAM-440, when business justification per IAM-001 need-to-know principle is absent or inadequate, when approval workflows per IAM-440 are bypassed or circumvented allowing unauthorized provisioning, when access is granted based on informal verbal requests without documented tickets per IAM-007(f)(i) formal evidence requirements, when terminated employees' access is not revoked timely per leaver process requirements, when employees changing roles retain unnecessary access from previous positions (privilege creep), or when dormant accounts per IAM-720 remain active beyond policy thresholds providing unauthorized access vectors. The risk is heightened when there is no HR system integration to trigger access revocation per leaver process, when access reviews per access review requirements are not conducted or are incomplete allowing inappropriate access to persist undetected, when requestor groups are not validated per authorized requestor principles, or when segregation of duties per IAM-002 is not enforced allowing requestors to approve their own access. Unauthorized access can also occur through technical account creation outside normal provisioning channels, through privilege escalation where users grant themselves additional access, or through exploitation of default accounts per IAM-242 if not properly disabled. The consequences are severe: unauthorized individuals accessing sensitive data including PII and financial information, insider threats where disgruntled former employees access systems after termination, fraud enabled by users having access beyond their legitimate job requirements per IAM-001, data breaches and exfiltration, compliance violations with regulatory requirements for access control, inability to demonstrate that access was properly authorized during audits of IAM-440 controls, and reputational damage from security incidents. For example, a developer might bypass approval workflows to grant themselves production database access violating IAM-002 SoD requirements, a terminated employee might retain database access for weeks after departure because leaver process was not executed, or a user might accumulate excessive access over time through role changes without access adjustment violating IAM-001 least privilege. This risk directly undermines the core IAM objectives per IAM-001 that access is based on need-to-know, granted according to Job Roles per IAM-015/016, and limited to systems and privileges required for Job Responsibilities, as well as the IAM-440 requirement that any account creation or modification can only be performed if approval has been obtained from appropriate authorities.
Mapped Control Title:
Comprehensive Access Authorization and Lifecycle Management (IAM-440, IAM-700/705/710/720, Entitlement Review Controls)
Control Description:
A comprehensive set of controls governs the complete access lifecycle from initial request through ongoing validation to eventual revocation, ensuring that access to Group Information and Technology Assets is granted only to authorized users with valid business rationale per IAM-440 objectives. At the provisioning stage, IAM-440 requires that any account creation or modification can only be performed if approval has been obtained: from People Leader or Information System Owner or Technology Infrastructure Owner for individual accounts per IAM-440(a), from Information System Owner or Technology Infrastructure Owner for generic accounts per IAM-440(b), and in line with applicable IAM procedures with all formal requirements met per IAM-440(c). All access provisioning and deprovisioning requests require formal requirements and evidence per IAM-007(f)(i). Access requests are reviewed and approved before granting access per access authorization requirements, ensuring only authorized users with valid business rationale can access respective Group Information and Technology Assets per control objectives. The approval workflow enforces segregation of duties where requestors cannot approve their own access per IAM-002, and approvals must be documented and retained as evidence per IAM-007(f)(i). At the deprovisioning stage, leaver process per IAM-700 ensures that when staff leaves the organization, logical access to Information Systems and Technology Infrastructure is removed before or on the Last Working Day or as per leaver process SLA, with reassignment of generic accounts owned by leaving staff per IAM-700(c) and verification that Group IT equipment is recovered per IAM-700(d). The process requires registration of leaving request ensuring notification to HR with Last Working Date details per IAM-700(a). For staff moving to new roles, mover process per IAM-705 ensures removal of no longer needed logical access held in current role per IAM-705(a), provisioning of needed access in new role per IAM-705(d), and conclusion before staff starts new role or per mover process SLA per IAM-705(e). Dormant account management per IAM-720 requires disabling or locking accounts that were not used for more than 90 calendar days in Information Systems and Technology Infrastructure with S-BIA rating 4-5 per IAM-720(a), or more than 180 calendar days for S-BIA rating 1-3 per IAM-720(b), as well as accounts with no owner (orphan accounts) per IAM-720(c). If disabling or locking is not technically feasible, accounts must be deleted per IAM-710 reference. Access reviews are initiated per entitlement review requirements every 6 months for privileged accounts and Information Systems rated S-BIA 5 and all Technology Infrastructure, and at least once per year for Information Systems rated S-BIA 4 and below. Access reviews per entitlement review controls ensure Staff accounts no longer required due to mover/leaver process or short-term temporary access are disabled, locked, or deleted, and dormant accounts are disabled, locked, or deleted if no longer needed per IAM-720 guidance, with evidence retained for review completion. Information System Owners and Technology Infrastructure Owners review and endorse access review results ensuring access is based on need-to-know per IAM-001 and access which is no longer needed is promptly revoked per control objectives. The combination of proactive deprovisioning through leaver and mover processes per IAM-700/705, reactive identification through dormant account detection per IAM-720, and periodic validation through access reviews per entitlement review requirements creates defense-in-depth ensuring unauthorized access is prevented at provisioning and detected and remediated if it occurs, maintaining alignment with the fundamental principle per IAM-001 that access to Group Information and Technology Assets is based on need-to-know and an Identity is granted access based on Job Role to ensure access is limited to systems and privileges required for delivering associated Job Responsibilities.
Related Key Questions:
What system or tool is used to submit and track database access requests per IAM-007(f)(i) formal requirements and evidence?
Can you demonstrate the access request workflow showing how approvals per IAM-440 are obtained from People Leader, Information System Owner, or Technology Infrastructure Owner before provisioning?
How do you ensure that access requests include business justification aligned with need-to-know principle per IAM-001 before approval per IAM-440?
What controls per IAM-002 prevent requestors from approving their own access requests (segregation of duties in approval process)?
Can you provide examples of recent access requests showing complete approval trail per IAM-440 and documented evidence per IAM-007(f)(i)?
Is there HR system integration to automatically trigger the leaver process per IAM-700 when employees are terminated? How does notification per IAM-700(a) work?
What is the SLA for revoking database access upon employee termination per IAM-700(b) leaver process requirement? Is it before or on Last Working Day?
Can you demonstrate that terminated employees' database access is removed per leaver process SLA per IAM-700(b)? Can you provide metrics on revocation timeliness?
How do you handle the mover process per IAM-705 when employees change roles? Is no longer needed access removed per IAM-705(a) and is the process concluded before staff starts new role per IAM-705(e)?
What is your dormant account policy per IAM-720? Are accounts inactive >90 days (S-BIA 4-5) or >180 days (S-BIA 1-3) disabled or locked per IAM-720(a)(b)?
How do you identify dormant accounts per IAM-720 and orphan accounts (accounts with no owner) per IAM-720(c)? What is the remediation process?
Are access reviews conducted per entitlement review requirements at required frequency (every 6 months for privileged accounts and S-BIA 5 systems, annually for S-BIA 4 and below)?
Can you provide evidence from the last 2-3 access review cycles showing completion, findings, and remediation per entitlement review controls?
Do access reviews per entitlement review controls verify that Staff accounts no longer required due to mover/leaver process or temporary access are disabled, locked, or deleted?
Are dormant accounts per IAM-720 identified and remediated during access reviews per entitlement review control guidance?
Do Information System Owners and Technology Infrastructure Owners review and endorse access review results per entitlement review requirements?
What happens if inappropriate access is identified during reviews? Is it remediated promptly per control objective that access no longer needed is promptly revoked?
How do you validate that only authorized requestor groups per authorized requestor principles can submit database access requests?
Can you demonstrate that access cannot be provisioned without proper approvals per IAM-440 through technical or procedural controls?
For privileged emergency account per IAM-440 note, is a valid corresponding incident ticket required for creation or enablement per IAM-440 requirement?
Control Design Effectiveness (CDE) Test Procedures:
CDE Test 1: Access Approval Workflow Design
Objective: Verify that access request and approval workflow per IAM-440 is designed to ensure access can only be provisioned with proper authorization.
Test Steps:
Request documentation of access request and approval workflow per IAM-440.
Verify workflow design includes mandatory approval requirements per IAM-440:
Individual account creation or modification requires approval from People Leader OR Information System Owner OR Technology Infrastructure Owner per IAM-440(a)
Generic account creation or modification requires approval from Information System Owner OR Technology Infrastructure Owner per IAM-440(b)
All requests must be in line with applicable IAM procedures with formal requirements met per IAM-440(c)
Review formal requirements and evidence per IAM-007(f)(i):
Access provisioning requests must be formally documented
Business justification per IAM-001 need-to-know must be included
All required approvals must be retained as evidence
Examine segregation of duties controls per IAM-002:
Workflow prevents requestor from being approver
Separate roles for access requestor, approver, and provisioner
Technical or procedural enforcement of segregation
Verify workflow design for different access types:
Standard user access approval path
Privileged access approval path (additional scrutiny)
Sensitive data access approval path (data owner approval)
Temporary or time-bound access approval and expiration
Review emergency access procedures per IAM-440 note:
For privileged emergency account creation or enablement, valid corresponding incident ticket must be present
Emergency access approval requirements
Post-implementation review of emergency access
Examine access request template or system:
Mandatory fields include: Requester, User for whom access requested, Job Role per IAM-015/016, Database and Access Profile requested, Business justification, Approver identification
System validation of required fields before submission
Verify workflow cannot be bypassed:
Technical controls prevent direct database account creation outside workflow
Audit logging of all account creation and modification per IAM-440
Detection mechanisms for unauthorized account creation
Review authorized requestor validation:
