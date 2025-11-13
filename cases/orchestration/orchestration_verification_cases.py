"""
Orchestration Verification Delegation Cases for CBR MCP Server
Examples: Delegating to karen for verification, parallel verification, TDD verification, infrastructure verification
"""

ORCHESTRATION_VERIFICATION_DELEGATION_CASES = [
    {
        "problem": """
After ui-developer completes the GoogleSignInButton component, show how to properly delegate to karen for verification.
""",
        "solution": """
The ui-developer has reported that the GoogleSignInButton component is complete.

According to the Execution Ritual and my agent directory, ui-developer is a requires-karen agent. I MUST delegate to karen for verification before proceeding.

<thinking>
As per my Execution Ritual (Step 2: Verify), I must delegate to karen. I will first search for verification delegation examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen verification ui component</query>
        <category>orchestration</category>
        <subcategory>verification</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` for verification of the UI component.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify GoogleSignInButton component</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the GoogleSignInButton component implementation meets all requirements</task_objective>
    <requirements>
The ui-developer has completed the GoogleSignInButton component.

## File to verify
src/components/auth/GoogleSignInButton.tsx

## Verification criteria

1. **Functionality**: Component correctly initiates Google OAuth flow
2. **Props**: Component accepts and uses onClick handler prop correctly
3. **Loading State**: Component displays loading indicator during authentication
4. **Error Handling**: Component gracefully handles and displays error states
5. **Code Quality**: Component follows project React patterns and conventions
6. **Styling**: Component uses Bootstrap classes consistent with other auth components
7. **Type Safety**: All TypeScript types are properly defined
8. **Accessibility**: Component includes proper ARIA attributes

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Briefly confirm what was verified

If INCOMPLETE:
- State "INCOMPLETE: [specific issue]"
- List specific issues that need to be fixed
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response. If karen returns "VERIFIED COMPLETE", I will proceed to the next step. If karen returns "INCOMPLETE", I will execute the Remediation Protocol.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "delegation",
            "verification",
            "karen",
            "ui-developer",
            "component",
            "requires-karen",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
The `ui-developer` and `firebase-backend-architect` have both completed their parallel tasks for the Google Sign-In feature. Show how to delegate parallel verification to karen.
""",
        "solution": """
The `ui-developer` (Track A) and `firebase-backend-architect` (Track B) have both reported completion.

My plan requires verification for both. I can delegate these two verification tasks to `karen` in parallel.

<thinking>
As per my Execution Ritual (Step 2: Verify), I must delegate to karen for both tracks. I will first search for parallel verification delegation examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen parallel verification</query>
        <category>orchestration</category>
        <subcategory>verification</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate *both* verification tasks to `karen` in parallel, one for each track.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify GoogleSignInButton component (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the GoogleSignInButton component (Track A) implementation.</task_objective>
    <requirements>
The ui-developer has completed the GoogleSignInButton component.

## This is Track A verification

## File to verify
src/components/auth/GoogleSignInButton.tsx

## Verification criteria
- **Functionality**: Component initiates OAuth flow correctly
- **Loading State**: Component displays loading indicator
- **Error Handling**: Component handles error states gracefully
- **Styling**: Component uses Bootstrap classes consistent with project

RESPOND WITH:
- "VERIFIED COMPLETE" if all criteria met
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify handleGoogleAuthToken function (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the `handleGoogleAuthToken` function (Track B) implementation.</task_objective>
    <requirements>
The firebase-backend-architect has completed the `handleGoogleAuthToken` function.

## This is Track B verification

## File to verify
functions/src/auth.ts

## Verification criteria
- **Functionality**: Function correctly processes a test Google Auth token
- **Token Validation**: Function verifies token signature and expiration
- **Firestore**: Function creates/updates user record in Firestore correctly
- **Return Value**: Function returns a valid custom auth token
- **Error Handling**: Function handles invalid or expired tokens appropriately

RESPOND WITH:
- "VERIFIED COMPLETE" if all criteria met
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for `karen` to return a status for *both* verification tasks before proceeding to the join phase (Code Review).
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "delegation",
            "verification",
            "karen",
            "parallel",
            "2-tracks",
            "ui-developer",
            "firebase-backend-architect",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After `tdd-test-engineer` completes writing the *failing tests* for the `last_login_ip` feature, show how to delegate to `karen` to verify they fail correctly.
""",
        "solution": """
The `tdd-test-engineer` has reported that the new tests for `last_login_ip` are complete.

The TDD process requires that these new tests *fail* before implementation begins. I must delegate to `karen` to verify this specific "failing" requirement.

<thinking>
As per my Execution Ritual (Step 2: Verify), I must delegate to karen for TDD verification. I will first search for TDD verification delegation examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen tdd failing tests verification</query>
        <category>orchestration</category>
        <subcategory>verification</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` to verify the failing tests meet TDD requirements.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify failing tests for last_login_ip</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the new tests for `last_login_ip` fail as expected (TDD red phase).</task_objective>
    <requirements>
The `tdd-test-engineer` has added new tests for a field that does not exist yet.

## File to verify
tests/test_user_repository.rs

## TDD Verification criteria

This is a TDD "Red Phase" verification. For this to be correct:

1. **New Tests MUST Fail**: The new tests for `last_login_ip` field MUST fail
   - Test for creating user with last_login_ip
   - Test for updating user's last_login_ip
   - Test for retrieving user with last_login_ip

2. **Existing Tests MUST Pass**: All pre-existing tests in the repository must still pass

3. **Failure Reason**: Tests should fail because the field doesn't exist yet, not due to syntax errors

## Response format

If VERIFIED COMPLETE (tests fail correctly):
- State "VERIFIED COMPLETE"
- Confirm "New tests failed as expected. Existing tests passed."

If INCOMPLETE:
- State "INCOMPLETE: [issue]"
- Report what went wrong (e.g., "New tests passed when they should fail" or "Existing tests broke")
    </requirements>
    <critical>This is TDD verification. The new tests MUST fail for this step to be complete.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `karen`'s response. If "VERIFIED COMPLETE" (tests failed correctly), I will proceed to the implementation step. If "INCOMPLETE", I will execute the Remediation Protocol.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "delegation",
            "verification",
            "karen",
            "tdd-test-engineer",
            "tdd",
            "red-phase",
            "failing-tests",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After `rust-developer` implements the `last_login_ip` field, show how to delegate to `karen` to verify the implementation (TDD green phase).
""",
        "solution": """
The `rust-developer` has reported that the `last_login_ip` field implementation is complete.

Now I must delegate to `karen` to verify that the previously-failing tests now pass (TDD green phase).

<thinking>
As per my Execution Ritual (Step 2: Verify), I must delegate to karen for TDD green phase verification. I will first search for verification delegation examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen tdd implementation verification</query>
        <category>orchestration</category>
        <subcategory>verification</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` to verify the implementation passes all tests.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify last_login_ip implementation</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the `last_login_ip` field implementation passes all tests (TDD green phase).</task_objective>
    <requirements>
The `rust-developer` has implemented the `last_login_ip` field in the User model and repository.

## Files to verify
- src/models/user.rs
- src/repositories/user_repository.rs

## TDD Green Phase verification criteria

1. **All Tests MUST Pass**: Every test in `tests/test_user_repository.rs` must pass
   - The previously-failing `last_login_ip` tests must now pass
   - All existing tests must still pass

2. **Implementation Quality**: Verify the implementation is correct
   - Field is properly defined in the User struct
   - Repository methods handle the field correctly
   - No compilation errors or warnings

## Response format

If VERIFIED COMPLETE (all tests pass):
- State "VERIFIED COMPLETE"
- Confirm "All tests passed. Implementation is correct."

If INCOMPLETE:
- State "INCOMPLETE: [issue]"
- Report which tests failed and why
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `karen`'s response. If "VERIFIED COMPLETE", I will proceed to the next step (migration script). If "INCOMPLETE", I will execute the Remediation Protocol.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "delegation",
            "verification",
            "karen",
            "rust-developer",
            "tdd",
            "green-phase",
            "implementation",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After `aws-devops-engineer` updates the CI/CD pipeline to use a new base image, show how to delegate to `karen` for infrastructure verification.
""",
        "solution": """
The `aws-devops-engineer` has reported that the `Dockerfile` and `ci.yml` have been updated to use the new `rust:1.79-slim` base image.

I must now delegate to `karen` to verify that the pipeline builds successfully before merging.

<thinking>
As per my Execution Ritual (Step 2: Verify), I must delegate to karen for infrastructure verification. I will first search for DevOps verification delegation examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen devops infrastructure ci-cd verification</query>
        <category>orchestration</category>
        <subcategory>verification</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` to verify the CI pipeline works with the new base image.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify CI pipeline with new base image</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the CI pipeline builds successfully with the new `rust:1.79-slim` base image.</task_objective>
    <requirements>
The `aws-devops-engineer` has updated the infrastructure files to use a new base image.

## Files changed
- Dockerfile
- .github/workflows/ci.yml

## Infrastructure verification criteria

1. **Trigger Build**: Trigger a new CI pipeline build
2. **Build Stage**: Verify the build stage completes successfully
   - Confirm the new base image `rust:1.79-slim` is pulled
   - Confirm all dependencies are available
   - Confirm compilation succeeds
3. **Test Stage**: Verify the test stage passes
4. **Lint Stage**: Verify the lint stage passes
5. **Build Logs**: Check logs for any warnings or issues

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Confirm "CI pipeline passed successfully with rust:1.79-slim base image."

If INCOMPLETE:
- State "INCOMPLETE: [issue]"
- Include the error from the failed pipeline stage
- Specify which stage failed (build/test/lint)
    </requirements>
    <critical>You must trigger and monitor the actual CI pipeline. Do not just review code.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `karen`'s response. If the pipeline fails ("INCOMPLETE"), I will execute the Remediation Protocol.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "delegation",
            "verification",
            "karen",
            "aws-devops-engineer",
            "infrastructure",
            "ci-cd",
            "docker",
            "devops",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After `tdd-test-engineer` completes tests for 4 parallel feature tracks in the Admin Dashboard, show how to delegate parallel verification to karen.
""",
        "solution": """
The `tdd-test-engineer` has completed tests for all 4 parallel feature tracks (User Management, Analytics, Export, Audit Logging).

I must delegate verification to `karen` for all 4 tracks in parallel.

<thinking>
As per my Execution Ritual (Step 2: Verify), I must delegate to karen for all 4 tracks. I will first search for parallel verification delegation examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen parallel 4-track verification</query>
        <category>orchestration</category>
        <subcategory>verification</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate verification to `karen` for all 4 tracks simultaneously.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify User Management tests (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the User Management CRUD tests (Track A) fail correctly.</task_objective>
    <requirements>
## This is Track A (User Management) TDD verification

The tdd-test-engineer has written tests for user management CRUD operations.

## File to verify
tests/test_admin_user_management.rs

## Verification criteria
- New tests for user CRUD operations MUST fail (feature not implemented yet)
- Existing tests must still pass
- Tests cover: create, read, update, delete users
- Tests verify admin permissions required

RESPOND WITH:
- "VERIFIED COMPLETE" if tests fail as expected
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>TDD verification - new tests must fail.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify Analytics tests (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the Analytics tests (Track B) fail correctly.</task_objective>
    <requirements>
## This is Track B (Analytics) TDD verification

The tdd-test-engineer has written tests for analytics data aggregation.

## File to verify
tests/test_admin_analytics.rs

## Verification criteria
- New tests for analytics MUST fail (feature not implemented yet)
- Existing tests must still pass
- Tests cover: user trends, active metrics, date filtering
- Tests verify data aggregation correctness

RESPOND WITH:
- "VERIFIED COMPLETE" if tests fail as expected
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>TDD verification - new tests must fail.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify Export tests (Track C)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the Export functionality tests (Track C) fail correctly.</task_objective>
    <requirements>
## This is Track C (Export) TDD verification

The tdd-test-engineer has written tests for data export functionality.

## File to verify
tests/test_admin_exports.rs

## Verification criteria
- New tests for exports MUST fail (feature not implemented yet)
- Existing tests must still pass
- Tests cover: CSV export, JSON export, data filtering, admin permissions
- Tests verify large dataset handling

RESPOND WITH:
- "VERIFIED COMPLETE" if tests fail as expected
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>TDD verification - new tests must fail.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify Audit Log tests (Track D)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the Audit Logging tests (Track D) fail correctly.</task_objective>
    <requirements>
## This is Track D (Audit Logging) TDD verification

The tdd-test-engineer has written tests for audit logging system.

## File to verify
tests/test_admin_audit_logs.rs

## Verification criteria
- New tests for audit logs MUST fail (feature not implemented yet)
- Existing tests must still pass
- Tests cover: action logging, immutability, search/filter, no sensitive data logged
- Tests verify comprehensive audit trail

RESPOND WITH:
- "VERIFIED COMPLETE" if tests fail as expected
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>TDD verification - new tests must fail.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `karen` to complete verification for all 4 tracks before proceeding to implementation steps.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "delegation",
            "verification",
            "karen",
            "parallel",
            "4-tracks",
            "tdd-test-engineer",
            "admin-dashboard",
            "complex",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After `31337` completes security fixes for 3 parallel tracks (SQL injection, rate limiting, log sanitization), show how to delegate parallel verification to karen.
""",
        "solution": """
The security specialist `31337` has completed all 3 security fixes in parallel (SQL injection, rate limiting, log sanitization).

I must delegate verification to `karen` for all 3 fixes in parallel.

<thinking>
As per my Execution Ritual (Step 2: Verify), I must delegate to karen for all 3 security fixes. I will first search for parallel security verification delegation examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen parallel security verification 31337</query>
        <category>orchestration</category>
        <subcategory>verification</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate verification to `karen` for all 3 security fixes simultaneously.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify SQL injection fix (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the SQL injection vulnerability fix (Track A) is working correctly.</task_objective>
    <requirements>
## This is Track A (SQL Injection Fix) verification

The security specialist 31337 has fixed the SQL injection vulnerability in the search functionality.

## Files to verify
- src/routes/search.rs
- tests/test_search_security.rs

## Verification criteria
- All security tests for SQL injection MUST pass
- Tests with injection attempts (e.g., "'; DROP TABLE--") are safely handled
- Parameterized queries are used throughout
- No existing search functionality is broken

RESPOND WITH:
- "VERIFIED COMPLETE" if fix is working correctly
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify rate limiting implementation (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the rate limiting implementation (Track B) is working correctly.</task_objective>
    <requirements>
## This is Track B (Rate Limiting) verification

The security specialist 31337 has implemented rate limiting middleware.

## Files to verify
- src/middleware/rate_limiter.rs
- tests/test_rate_limiting.rs

## Verification criteria
- All rate limiting tests MUST pass
- Requests within limit succeed (100/min general, 10/min for /login)
- Requests exceeding limit return 429 status
- Rate limits are tracked per IP address
- Rate limits reset correctly after time window

RESPOND WITH:
- "VERIFIED COMPLETE" if implementation is working correctly
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify log sanitization implementation (Track C)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the log sanitization implementation (Track C) is working correctly.</task_objective>
    <requirements>
## This is Track C (Log Sanitization) verification

The security specialist 31337 has implemented log sanitization and moved API keys to secure storage.

## Files to verify
- src/middleware/log_sanitizer.rs
- src/config.rs
- tests/test_log_security.rs

## Verification criteria
- All log security tests MUST pass
- API keys are redacted in log output (shown as "***")
- Passwords are never logged
- Auth tokens are sanitized
- API keys moved from env vars to secure storage (AWS Secrets Manager)
- Config loads secrets securely

RESPOND WITH:
- "VERIFIED COMPLETE" if implementation is working correctly
- "INCOMPLETE: [issue]" if problems found
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `karen` to complete verification for all 3 security fixes before proceeding to the security-auditor re-audit step.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "delegation",
            "verification",
            "karen",
            "parallel",
            "3-tracks",
            "31337",
            "security",
            "security-fixes",
            "vulnerability",
            "cbr-retrieval",
        ],
    },
]