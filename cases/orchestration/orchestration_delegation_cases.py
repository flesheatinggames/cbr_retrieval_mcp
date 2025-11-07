"""
Orchestration Delegation Cases for CBR MCP Server
Examples: Proper delegation format, multi-agent coordination, parallel task delegation, workflow handoffs
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
    <task_objective>Investigate and identify the performance bottleneck in the `/api/v1/analytics/report` endpoint.</task_objective>
    <requirements>
        - You must analyze the code for the endpoint, located in `src/routes/analytics.rs`.
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
        - Tests must assert that the logic correctly applies the theme (e.D., by adding/removing a class from `document.body`).
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
]