"""
Orchestration Delegation Cases for CBR MCP Server
Examples: Proper delegation format, multi-agent coordination, parallel task delegation, workflow handoffs
Enhanced version with more parallel delegation examples
"""

ORCHESTRATION_DELEGATION_CASES = [
    {
        "problem": """
User: "I need to add Google Sign-In to our application."

The orchestrator has created a parallel plan. Now show how to properly delegate the parallel tasks to their respective agents.
""",
        "solution": """
The approved parallel plan has these tracks:
*Track A (UI):*
1. Create GoogleSignInButton component (ui-developer)
2. Verify UI Component (karen)
*Track B (Backend):*
3. Create handleGoogleAuthToken function (firebase-backend-architect)
4. Verify Backend Function (karen)
*Join Phase:*
5. Code review (code-reviewer)

I will now delegate the first task of each parallel track (Step 1 and Step 3).
As per my Execution Ritual, I must first search for delegation examples.

<thinking>
My approved plan has two parallel pending tasks. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation parallel examples</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to the `ui-developer` for Track A and the `firebase-backend-architect` for Track B, ensuring both match the `delegation_format` template.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Create GoogleSignInButton component (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>ui-developer</agent_name>
    <task_objective>Create the GoogleSignInButton React component that initiates Google OAuth flow</task_objective>
    <requirements>
        - Component must be located in src/components/auth/GoogleSignInButton.tsx
        - Component must accept onClick handler as prop
        - Component must display loading state during authentication
        - Component must handle error states gracefully
        - Component must follow the project's React component patterns
        - Component must use Bootstrap styling consistent with other auth components
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>firebase-backend-architect</subagent_type>
        <description>Create handleGoogleAuthToken function (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>firebase-backend-architect</agent_name>
    <task_objective>Create the `handleGoogleAuthToken` Cloud Function to securely process the token</task_objective>
    <requirements>
        - Function must be located in `functions/src/auth.ts`
        - Function must receive a Google Auth token via an HTTPS request
        - Function must verify the token's signature and expiration
        - Function must create or update a user record in Firestore
        - Function must return a custom auth token for the user
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After both the `ui-developer` and `firebase-backend-architect` complete their work, I will proceed to their respective verification steps (Step 2 and Step 4).
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "ui-developer",
            "firebase-backend-architect",
            "parallel",
            "google-auth",
            "cbr-retrieval",
            "ritual",
        ],
    },
    {
        "problem": """
User: "Add a last_login_ip field to the User model in the database."

The orchestrator has created a sequential TDD plan. Show how to properly delegate the *first* task to the `tdd-test-engineer`.
""",
        "solution": """
The approved sequential plan is:
1. Write Repository Tests (tdd-test-engineer)
2. Verify Tests (karen)
3. Update Code (rust-developer)
4. Verify Code (karen)
5. Write Migration Script (aws-devops-engineer)
6. Verify Migration Script (karen)
7. Final Code Review (code-reviewer)

I will now delegate the first task (Step 1) to the `tdd-test-engineer`.

<thinking>
My approved plan has a pending task. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation tdd-test-engineer database</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to the `tdd-test-engineer`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Repository Tests for last_login_ip</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for the `UserRepository` to handle a new `last_login_ip` field.</task_objective>
    <requirements>
        - The tests must be located in `tests/test_user_repository.rs`.
        - Write a test case for creating a user and asserting the `last_login_ip` is saved.
        - Write a test case for updating a user's `last_login_ip` and asserting the change.
        - Write a test case for retrieving a user and asserting the `last_login_ip` is correctly loaded.
        - The tests should (and must) fail initially, as the field does not exist yet.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After the `tdd-test-engineer` completes this work, I will delegate to `karen` for verification.
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "tdd-test-engineer",
            "sequential",
            "database",
            "cbr-retrieval",
            "ritual",
        ],
    },
    {
        "problem": """
User: "The /api/v1/analytics/report endpoint is too slow. Find the bottleneck and optimize it."

The orchestrator has created an investigation plan. Show how to delegate this task to the `debug-specialist`.
""",
        "solution": """
The approved investigation plan is:
1. Investigate Bottleneck (debug-specialist)

I will now delegate this task.

<thinking>
My approved plan has a pending task. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation debug-specialist investigation</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to the `debug-specialist`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>debug-specialist</subagent_type>
        <description>Investigate performance of /api/v1/analytics/report</description>
        <prompt>
<delegate_task>
    <agent_name>debug-specialist</agent_name>
    <task_objective>Identify the root cause of the slow performance on the `/api/v1/analytics/report` endpoint.</task_objective>
    <requirements>
        - Use profiling tools to identify slow database queries (e.g., N+1 problems) or inefficient computations.
        - Your final report must include:
            1. The specific root cause of the slowness.
            2. A clear, actionable recommendation for how to fix it (e.g., "Add a database index," "Refactor to a single query," "Implement caching").
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

Once the `debug-specialist` provides the root cause, I will formulate a new plan for remediation.
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "debug-specialist",
            "investigation",
            "performance",
            "cbr-retrieval",
            "ritual",
        ],
    },
    {
        "problem": """
User: "Add a dark mode toggle to the UI that persists the user's preference."

The orchestrator has created a 3-track parallel plan. Show how to properly delegate the first task of *all three* tracks.
""",
        "solution": """
The approved parallel plan has these tracks:
*Track A (Backend):*
1. Backend API Tests (tdd-test-engineer)
...
*Track B (UI Component):*
5. Frontend UI Tests (tdd-test-engineer)
...
*Track C (Client Logic):*
9. Frontend Logic Tests (tdd-test-engineer)
...
*Join Phase:*
13. Code Review (code-reviewer)

I will now delegate the first task of all three parallel tracks (Steps 1, 5, and 9) to the `tdd-test-engineer`.

<thinking>
My approved plan has three parallel pending tasks. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation parallel 3-track tdd</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate all three TDD tasks to the `tdd-test-engineer` simultaneously.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Backend API Tests (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for the new user preferences API endpoint `/api/user/preferences`.</task_objective>
    <requirements>
        - This is for Track A (Backend).
        - Tests must assert that the endpoint correctly saves a theme preference (e.g., 'dark') to the database.
        - Tests must assert that the endpoint returns the saved preference.
        - These tests should fail until the endpoint is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Frontend UI Tests (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for the new `<ThemeToggle>` React component.</task_objective>
    <requirements>
        - This is for Track B (UI Component).
        - Tests must assert that the component renders correctly.
        - Tests must assert that clicking the toggle correctly calls its `onToggle` prop.
        - These tests should fail until the component is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Frontend Logic Tests (Track C)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for the client-side theme management logic.</task_objective>
    <requirements>
        - This is for Track C (Client Logic).
        - Tests must mock the API call and assert that the logic correctly calls the `/api/user/preferences` endpoint.
        - Tests must assert that the logic correctly applies the theme (e.g., by adding/removing a class from `document.body`).
        - These tests should fail until the logic is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for the `tdd-test-engineer` to complete all three tasks before proceeding to their respective verification and implementation steps.
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "tdd-test-engineer",
            "parallel",
            "full-stack",
            "dark-mode",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Add server-side validation to the user registration endpoint for password strength."

The implementation and verification steps are complete. Show how to delegate the *final* task to the `security-auditor`.
""",
        "solution": """
The approved plan is:
1. Write Failing Tests (tdd-test-engineer) - COMPLETED
2. Verify Failing Tests (karen) - COMPLETED
3. Implement Validation (rust-developer) - COMPLETED
4. Verify Implementation (karen) - COMPLETED
5. Security Audit (security-auditor) - PENDING

All implementation steps are complete. I will now delegate the final task (Step 5) to the `security-auditor`.

<thinking>
My plan's final task is pending. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation finalization blocking-authority security-auditor</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples for finalization agents. I will now delegate to the `security-auditor`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>security-auditor</subagent_type>
        <description>Audit new password strength validation logic</description>
        <prompt>
<delegate_task>
    <agent_name>security-auditor</agent_name>
    <task_objective>Audit the new password strength validation logic on the user registration endpoint for security vulnerabilities.</task_objective>
    <requirements>
        - Review the implementation file `src/routes/auth.rs`.
        - Verify that the validation is strictly enforced on the server-side and cannot be bypassed.
        - Check for Regular Expression Denial of Service (ReDoS) vulnerabilities in the password strength regex.
        - Ensure that error messages for weak passwords are generic and do not leak information about *why* it was weak (e.g., "Password does not meet requirements" is good; "Password is missing a number" is bad).
    </requirements>
    <critical>You are a BLOCKING AUTHORITY. The task cannot be completed until you respond with "APPROVED". Respond with "FAILED" if critical issues are found.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for the `security-auditor`'s response. I am FORBIDDEN from marking the task complete until this agent provides "APPROVED" status.
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "security-auditor",
            "finalization",
            "blocking-authority",
            "security",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Build an admin dashboard with user management, analytics, export functionality, and audit logging."

The orchestrator has created a 4-track parallel plan. Show how to properly delegate the first task of *all four* tracks simultaneously.
""",
        "solution": """
The approved parallel plan has these tracks:
*Track A (User Management):*
1. Test User CRUD (tdd-test-engineer)
2. Verify User Tests (karen)
3. Implement User Management UI (ui-developer)
4. Verify User UI (karen)
5. Implement User Management API (firebase-backend-architect)
6. Verify User API (karen)

*Track B (Analytics Charts):*
7. Test Analytics (tdd-test-engineer)
8. Verify Analytics Tests (karen)
9. Implement Analytics UI (ui-developer)
10. Verify Analytics UI (karen)
11. Implement Analytics API (firebase-backend-architect)
12. Verify Analytics API (karen)

*Track C (Export Functionality):*
13. Test Exports (tdd-test-engineer)
14. Verify Export Tests (karen)
15. Implement Export Service (firebase-backend-architect)
16. Verify Export Service (karen)

*Track D (Audit Logging):*
17. Test Audit Log (tdd-test-engineer)
18. Verify Audit Tests (karen)
19. Implement Audit System (firebase-backend-architect)
20. Verify Audit System (karen)

*Finalization Phase:*
21. Security Audit (security-auditor)
22. Final Code Review (code-reviewer)

I will now delegate the first task of all four parallel tracks (Steps 1, 7, 13, and 17) to the `tdd-test-engineer`.

<thinking>
My approved plan has four parallel pending tasks. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation parallel 4-track admin dashboard complex</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate all four TDD tasks to the `tdd-test-engineer` simultaneously. This is the most complex parallel delegation with 4 independent feature tracks.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write User CRUD Tests (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write comprehensive tests for user management CRUD operations in the admin dashboard.</task_objective>
    <requirements>
        - This is for Track A (User Management).
        - Tests must cover creating new users with validation.
        - Tests must cover reading/listing users with pagination.
        - Tests must cover updating user information (email, roles, status).
        - Tests must cover deleting users with proper cascading.
        - Tests must verify admin-level permissions are required.
        - These tests should fail until the feature is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Analytics Tests (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for analytics data aggregation and charting functionality.</task_objective>
    <requirements>
        - This is for Track B (Analytics Charts).
        - Tests must cover user registration trends over time.
        - Tests must cover active user metrics and daily/weekly/monthly aggregations.
        - Tests must verify data is correctly filtered by date ranges.
        - Tests must verify proper handling of missing data points.
        - These tests should fail until the analytics system is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Export Tests (Track C)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for data export functionality in multiple formats.</task_objective>
    <requirements>
        - This is for Track C (Export Functionality).
        - Tests must verify CSV export generates valid format with proper escaping.
        - Tests must verify JSON export includes all required fields.
        - Tests must verify exports respect data filtering (date ranges, user roles).
        - Tests must verify large datasets are handled efficiently (streaming).
        - Tests must verify admin permissions are required for exports.
        - These tests should fail until export functionality is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Audit Log Tests (Track D)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for comprehensive audit logging system.</task_objective>
    <requirements>
        - This is for Track D (Audit Logging).
        - Tests must verify all admin actions (create, update, delete) are logged.
        - Tests must verify logs include timestamp, admin user, action type, and affected entity.
        - Tests must verify logs are immutable (cannot be modified or deleted).
        - Tests must verify audit log search and filtering functionality.
        - Tests must verify sensitive data (passwords) is never logged.
        - These tests should fail until the audit system is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for the `tdd-test-engineer` to complete all four test suites before proceeding to their respective verification and implementation steps in each track.
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "tdd-test-engineer",
            "parallel",
            "4-tracks",
            "admin-dashboard",
            "complex",
            "multi-feature",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Remediate the security findings from our latest audit: SQL injection vulnerability in search, missing rate limiting, and exposed API keys in logs."

The orchestrator has created a 3-track parallel plan for security remediation. Show how to delegate the first task of all three tracks (TDD phase).
""",
        "solution": """
The approved parallel plan has these tracks:
*Track A (SQL Injection Fix):*
1. Test SQL Fix (tdd-test-engineer)
2. Verify SQL Tests (karen)
3. Fix SQL Injection (31337)
4. Verify SQL Fix (karen)

*Track B (Rate Limiting):*
5. Test Rate Limiting (tdd-test-engineer)
6. Verify Rate Limit Tests (karen)
7. Implement Rate Limiting (31337)
8. Verify Rate Limiting (karen)

*Track C (API Key Protection):*
9. Test Log Sanitization (tdd-test-engineer)
10. Verify Log Tests (karen)
11. Sanitize Logs (31337)
12. Verify Log Sanitization (karen)

*Finalization Phase:*
13. Security Audit (security-auditor)
14. Final Code Review (code-reviewer)

I will now delegate the first task of all three parallel tracks (Steps 1, 5, and 9) to the `tdd-test-engineer`.

<thinking>
My approved plan has three parallel pending tasks for security remediation. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation parallel security remediation vulnerability</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate all three security-focused TDD tasks to the `tdd-test-engineer` simultaneously.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write SQL Injection Fix Tests (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for SQL injection vulnerability fixes in the search functionality.</task_objective>
    <requirements>
        - This is for Track A (SQL Injection Fix).
        - Tests must verify that search queries with SQL injection attempts (e.g., "'; DROP TABLE users--") are safely handled.
        - Tests must verify that parameterized queries are used instead of string concatenation.
        - Tests must verify that special characters in user input are properly escaped.
        - Tests must verify that search results are correct for legitimate queries.
        - These tests should initially pass for injection attempts (proving the vulnerability exists) then fail after the fix.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Rate Limiting Tests (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests for rate limiting enforcement on API endpoints.</task_objective>
    <requirements>
        - This is for Track B (Rate Limiting).
        - Tests must verify that requests within the rate limit succeed (e.g., 100 requests per minute).
        - Tests must verify that requests exceeding the rate limit return 429 (Too Many Requests) status.
        - Tests must verify that rate limits are tracked per IP address or API key.
        - Tests must verify that rate limits reset after the time window expires.
        - Tests must verify that critical endpoints like /login have stricter limits.
        - These tests should fail until rate limiting middleware is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write Log Sanitization Tests (Track C)</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write tests to verify that sensitive information is never exposed in application logs.</task_objective>
    <requirements>
        - This is for Track C (API Key Protection).
        - Tests must verify that API keys are redacted from log output (e.g., "key=***" instead of actual value).
        - Tests must verify that passwords are never logged, even in error scenarios.
        - Tests must verify that authentication tokens are sanitized in logs.
        - Tests must verify that log sanitization works for structured logs (JSON) and text logs.
        - Tests must verify that API keys are moved from environment variables to secure secret management.
        - These tests should fail until log sanitization is implemented.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for the `tdd-test-engineer` to complete all three security test suites before proceeding to their respective verification and remediation steps in each track.
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "tdd-test-engineer",
            "parallel",
            "3-tracks",
            "security",
            "remediation",
            "vulnerability",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Remediate the security findings from our latest audit: SQL injection vulnerability in search, missing rate limiting, and exposed API keys in logs."

The TDD tests are complete and verified for all three tracks. Show how to delegate the implementation tasks to the security specialist `31337` for all three tracks in parallel.
""",
        "solution": """
The approved parallel plan has these tracks:
*Track A (SQL Injection Fix):*
1. Test SQL Fix (tdd-test-engineer) - COMPLETED
2. Verify SQL Tests (karen) - COMPLETED
3. Fix SQL Injection (31337) - PENDING
4. Verify SQL Fix (karen)

*Track B (Rate Limiting):*
5. Test Rate Limiting (tdd-test-engineer) - COMPLETED
6. Verify Rate Limit Tests (karen) - COMPLETED
7. Implement Rate Limiting (31337) - PENDING
8. Verify Rate Limiting (karen)

*Track C (API Key Protection):*
9. Test Log Sanitization (tdd-test-engineer) - COMPLETED
10. Verify Log Tests (karen) - COMPLETED
11. Sanitize Logs (31337) - PENDING
12. Verify Log Sanitization (karen)

All TDD tests are complete and verified. I will now delegate the implementation tasks (Steps 3, 7, and 11) to the security specialist `31337` in parallel.

<thinking>
My approved plan has three parallel pending implementation tasks. I am now executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation 31337 security fixes parallel</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate all three security fix implementations to `31337` simultaneously. This demonstrates delegating multiple parallel tasks to the same specialized security agent.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Fix SQL Injection Vulnerability (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>31337</agent_name>
    <task_objective>Remediate the SQL injection vulnerability in the search functionality by implementing parameterized queries.</task_objective>
    <requirements>
        - This is for Track A (SQL Injection Fix).
        - Replace all string concatenation in search queries with parameterized queries or prepared statements.
        - The search implementation is located in `src/routes/search.rs`.
        - Ensure all user input is sanitized and validated before database operations.
        - Add input validation to reject obviously malicious patterns.
        - All existing tests in `tests/test_search_security.rs` must pass after your implementation.
        - Do not break existing legitimate search functionality.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Implement Rate Limiting (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>31337</agent_name>
    <task_objective>Implement rate limiting middleware to prevent abuse of API endpoints.</task_objective>
    <requirements>
        - This is for Track B (Rate Limiting).
        - Implement rate limiting middleware in `src/middleware/rate_limiter.rs`.
        - Use a sliding window algorithm with Redis or in-memory store for tracking.
        - Configure limits: 100 requests/minute for general endpoints, 10 requests/minute for /login.
        - Return 429 status code with Retry-After header when limit is exceeded.
        - Track limits per IP address, with ability to track by API key for authenticated requests.
        - All tests in `tests/test_rate_limiting.rs` must pass after your implementation.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Implement Log Sanitization (Track C)</description>
        <prompt>
<delegate_task>
    <agent_name>31337</agent_name>
    <task_objective>Implement log sanitization to prevent exposure of sensitive data and move API keys to secure storage.</task_objective>
    <requirements>
        - This is for Track C (API Key Protection).
        - Implement log sanitization middleware in `src/middleware/log_sanitizer.rs`.
        - Create a sanitization function that redacts: API keys, passwords, auth tokens, credit card numbers, SSNs.
        - Replace sensitive values with "***" in log output while preserving log structure.
        - Apply sanitization to both structured logs (JSON) and text logs.
        - Move API keys from environment variables to AWS Secrets Manager or similar secure storage.
        - Update configuration loading in `src/config.rs` to retrieve secrets securely.
        - All tests in `tests/test_log_security.rs` must pass after your implementation.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for the security specialist `31337` to complete all three remediation implementations before proceeding to their respective verification steps (Steps 4, 8, and 12).
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "31337",
            "security-specialist",
            "parallel",
            "3-tracks",
            "security-fixes",
            "implementation",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Build an admin dashboard with user management, analytics, export functionality, and audit logging."

All four parallel tracks have completed their implementation and verification. Show how to delegate the finalization tasks (security audit and code review) which join all tracks.
""",
        "solution": """
The approved parallel plan has these tracks:
*Track A (User Management):*
1-6. [All steps COMPLETED]

*Track B (Analytics Charts):*
7-12. [All steps COMPLETED]

*Track C (Export Functionality):*
13-16. [All steps COMPLETED]

*Track D (Audit Logging):*
17-20. [All steps COMPLETED]

*Finalization Phase:*
21. Security Audit (security-auditor) - PENDING
22. Final Code Review (code-reviewer) - PENDING

All four parallel implementation tracks are complete. I will now delegate the finalization tasks which join all tracks together.

<thinking>
All parallel tracks are complete. I am now entering the Finalization Phase and must delegate to BLOCKING AUTHORITY agents. I am executing Step 1 of the Execution Ritual: Delegate. This ritual requires me to first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation finalization security-auditor code-reviewer blocking</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples for finalization agents. I will now delegate to both `security-auditor` and `code-reviewer`. Note that `security-auditor` is a BLOCKING AUTHORITY because this is an admin dashboard with privileged access.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>security-auditor</subagent_type>
        <description>Security Audit of Complete Admin Dashboard</description>
        <prompt>
<delegate_task>
    <agent_name>security-auditor</agent_name>
    <task_objective>Conduct a comprehensive security audit of the complete admin dashboard implementation across all four feature tracks.</task_objective>
    <requirements>
        - Review all code from Track A (User Management), Track B (Analytics), Track C (Export), and Track D (Audit Logging).
        - Verify that all admin functionality requires proper authentication and authorization.
        - Check for SQL injection vulnerabilities in user management queries.
        - Verify that analytics data cannot be accessed by non-admin users.
        - Ensure export functionality validates permissions and limits data exposure.
        - Verify that audit logs are immutable and cannot be tampered with.
        - Check for Cross-Site Scripting (XSS) vulnerabilities in the UI.
        - Verify that session management is secure (proper timeouts, CSRF protection).
        - Ensure sensitive data (passwords, API keys) is never logged or exposed.
        - Review the admin dashboard for proper role-based access control (RBAC).
    </requirements>
    <critical>You are a BLOCKING AUTHORITY. This task cannot be marked complete until you respond with "APPROVED". Respond with "FAILED" if critical security issues are found.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for the `security-auditor`'s response. I am FORBIDDEN from delegating to `code-reviewer` or marking the task complete until `security-auditor` provides "APPROVED" status.

After security audit approval, I will then delegate to `code-reviewer` for the final code review (Step 22).
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "security-auditor",
            "finalization",
            "join-phase",
            "blocking-authority",
            "admin-dashboard",
            "4-tracks-complete",
            "cbr-retrieval",
        ],
    },
]