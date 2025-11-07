"""
Orchestration Remediation Cases for CBR MCP Server
Examples: Handling failed verification, remediation workflow, recovery protocols, cbr-retrieval, parallel remediation
"""

ORCHESTRATION_REMEDIATION_CASES = [
    {
        "problem": """
karen returned "INCOMPLETE: The button lacks a proper loading state." Show how to execute the Remediation Protocol.
""",
        "solution": """
Karen has returned "INCOMPLETE" which is a MANDATORY REMEDIATION TRIGGER.

I MUST now execute the Remediation Ritual:

## Step 1: Announce the Deviation

I have an update: karen has reviewed the GoogleSignInButton and found an issue. The button is missing a loading state during authentication. Per the Remediation Protocol, I am adding remedial steps to address this issue.

## Step 2: Formulate Remedial Tasks

<thinking>
As per my Remediation Ritual, I must first search for remediation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration remediation verification incomplete</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the remediation cases, I will formulate remedial tasks:
1. Delegate back to ui-developer to add the loading state
2. Delegate to karen to re-verify after the fix
</thinking>

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            "Create UI Component: ui-developer",
            "Verify UI Component: karen",
            "Fix: Add loading state to GoogleSignInButton: ui-developer",
            "Re-Verify UI Component: karen",
            "Create Backend Function: firebase-backend-architect",
            "Verify Backend Function: karen",
            "Final Code Review: code-reviewer"
        ]
    </tool>
</tool_code>

CRITICAL: I have NOT altered the original approved todos from the Plan of Record. I have ADDED new remedial tasks ("Fix..." and "Re-Verify...") immediately after the failed step, using the correct '[Task]: [Agent]' format.

## Step 4: Announce the New Plan

The remedial steps have been added to the plan:
- Step 3 (NEW): Fix the loading state issue
- Step 4 (NEW): Re-verify the component

## Step 5: Proceed with Remediation

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Add loading state to GoogleSignInButton</description>
        <prompt>
<delegate_task>
    <agent_name>ui-developer</agent_name>
    <task_objective>Add a loading state indicator to the GoogleSignInButton component</task_objective>
    <requirements>
        - Add a loading prop or state to track authentication in progress
        - Display a spinner or loading indicator when loading is true
        - Disable the button during loading to prevent multiple clicks
        - Ensure loading state is accessible (aria-busy attribute)
        - Maintain all existing functionality
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I am now waiting for the ui-developer to complete the fix before delegating to karen for re-verification.

**Completion Blocking**: I am FORBIDDEN from declaring task completion or proceeding to the next original step until:
1. The remedial fix is complete
2. Karen re-verifies and returns "VERIFIED COMPLETE"
3. All blocking issues are resolved
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": [
            'orchestration',
            'remediation',
            'karen',
            'incomplete',
            'ui',
            'verification-failure',
            'workflow',
            'cbr-retrieval',
            'ritual',
        ]
    },
    {
        "problem": """
code-reviewer returned "FAILED: Found 3 critical issues" after implementation was complete. Show the Remediation Protocol for code review failures.
""",
        "solution": """
code-reviewer has returned "FAILED" which is a MANDATORY REMEDIATION TRIGGER.

Code-reviewer is a BLOCKING AUTHORITY. I CANNOT declare task completion until code-reviewer approves.

## Step 1: Announce the Deviation

I have an update: code-reviewer has reviewed the Google Sign-In implementation and found 3 critical issues that need to be addressed:

1. Missing error handling for network failures (UI)
2. Token not validated before use (Backend)
3. Inconsistent naming conventions (UI)

Per the Remediation Protocol, I am adding remedial steps to fix these issues.

## Step 2: Formulate Remedial Tasks

<thinking>
As per my Remediation Ritual, I must first search for remediation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration remediation code-reviewer failed parallel</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the remediation cases, I will formulate parallel remedial tasks. The UI issues (error handling, naming) can be fixed in one track, and the backend issue (token validation) in another.

*Track A (UI Fixes):*
1. Fix: Add network error handling (ui-developer)
2. Fix: Correct naming conventions (ui-developer)

*Track B (Backend Fix):*
3. Fix: Add backend token validation (firebase-backend-architect)

*Join Phase:*
4. Verify all fixes (karen)
5. Re-review all code (code-reviewer)
</thinking>

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            "Create UI Component: ui-developer",
            "Verify UI Component: karen",
            "Create Backend Function: firebase-backend-architect",
            "Verify Backend Function: karen",
            "Final Code Review: code-reviewer",
            "Fix (UI): Add network error handling: ui-developer",
            "Fix (UI): Correct naming conventions: ui-developer",
            "Fix (Backend): Add token validation: firebase-backend-architect",
            "Verify All Fixes: karen",
            "Re-Review Code: code-reviewer"
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

The remedial steps have been added to the plan. I will run the UI and Backend fixes in parallel:

*Track A (UI):*
- Step 6 (NEW): Fix network error handling
- Step 7 (NEW): Fix naming conventions

*Track B (Backend):*
- Step 8 (NEW): Fix token validation

*Join Phase:*
- Step 9 (NEW): Verify all fixes
- Step 10 (NEW): Re-review the code

## Step 5: Proceed with Remediation (Parallel Delegation)

<thinking>
I will now delegate the first task of each parallel track.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Fix code review UI issues</description>
        <prompt>
<delegate_task>
    <agent_name>ui-developer</agent_name>
    <task_objective>Fix the 2 critical UI issues identified by code-reviewer.</task_objective>
    <requirements>
        Critical issues to fix:

        1. Missing error handling for network failures
           - Add try-catch blocks for network requests
           - Display user-friendly error messages

        2. Inconsistent naming conventions
           - Rename variables/functions in the UI code to follow project conventions
           - Update all references consistently

        - Maintain all existing functionality
        - Ensure all tests still pass
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>firebase-backend-architect</subagent_type>
        <description>Fix code review backend issue</description>
        <prompt>
<delegate_task>
    <agent_name>firebase-backend-architect</agent_name>
    <task_objective>Fix the 1 critical backend issue identified by code-reviewer.</task_objective>
    <requirements>
        Critical issue to fix:

        1. Token not validated before use
           - In the `handleGoogleAuthToken` function, add logic to validate the incoming token format and expiration before processing it.
           - Handle invalid tokens gracefully and return a proper error response.

        - Maintain all existing functionality
        - Ensure all tests still pass
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for both tracks to complete, then delegate to karen for verification, then back to code-reviewer for re-review.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": [
            'orchestration',
            'remediation',
            'code-reviewer',
            'failed',
            'blocking-authority',
            'critical-issues',
            'workflow',
            'cbr-retrieval',
            'ritual',
            'parallel',
        ]
    },
    {
        "problem": """
security-auditor returned "FAILED: Critical ReDoS vulnerability found in password regex." Show the Remediation Protocol.
""",
        "solution": """
security-auditor has returned "FAILED" which is a MANDATORY REMEDIATION TRIGGER.

This agent is a BLOCKING AUTHORITY. The task cannot be completed until the `security-auditor` responds with "APPROVED".

## Step 1: Announce the Deviation

I have an update: `security-auditor` has reviewed the password validation logic and found a critical security vulnerability: The regular expression used for password strength is susceptible to a Regular Expression Denial of Service (ReDoS) attack.

Per the Remediation Protocol, I am adding remedial steps to fix this vulnerability.

## Step 2: Formulate Remedial Tasks

<thinking>
As per my Remediation Ritual, I must first search for remediation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration remediation security-auditor failed vulnerability</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the remediation cases, I will formulate remedial tasks. Per the agent directory, security implementation tasks are delegated to `31337`.

1. Fix: Remediate ReDoS vulnerability (Agent: `31337`, requires `karen`)
2. Verification: Verify the fix (Agent: `karen`)
3. Re-Audit: Re-run security audit (Agent: `security-auditor`)
</thinking>

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            "Write Failing Tests: tdd-test-engineer",
            "Verify Failing Tests: karen",
            "Implement Validation: rust-developer",
            "Verify Implementation: karen",
            "Security Audit: security-auditor",
            "Fix: Remediate ReDoS vulnerability: 31337",
            "Verify Security Fix: karen",
            "Re-Audit Security: security-auditor"
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

The remedial steps have been added to the plan:
- Step 6 (NEW): Fix the ReDoS vulnerability
- Step 7 (NEW): Verify the fix
- Step 8 (NEW): Re-run the security audit

## Step 5: Proceed with Remediation

<thinking>
I will now delegate the first remedial task to `31337`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Fix ReDoS vulnerability in password regex</description>
        <prompt>
<delegate_task>
    <agent_name>31337</agent_name>
    <task_objective>Fix the ReDoS vulnerability in the password strength regex in `src/routes/auth.rs`.</task_objective>
    <requirements>
        - You must rewrite the regular expression to make it non-vulnerable to ReDoS.
        - Ensure the new regex still enforces the original password strength requirements (e.g., length, uppercase, number, special character).
        - Add tests that specifically target the ReDoS vulnerability to ensure it is resolved.
        - All existing tests must continue to pass.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `31337` to complete the fix, then delegate to `karen` to verify, and finally back to `security-auditor` for the blocking re-audit.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": [
            'orchestration',
            'remediation',
            'security-auditor',
            '31337',
            'failed',
            'blocking-authority',
            'vulnerability',
            'redos',
            'cbr-retrieval',
            'ritual',
        ]
    },
    {
        "problem": """
karen returned "INCOMPLETE: The CI pipeline failed to build with the new base image." Show the Remediation Protocol.
""",
        "solution": """
karen has returned "INCOMPLETE" which is a MANDATORY REMEDIATION TRIGGER. This was a verification step for an infrastructure change.

## Step 1: Announce the Deviation

I have an update: karen has verified the `aws-devops-engineer`'s changes to the CI/CD pipeline and found an issue: The pipeline failed to build using the new `rust:1.79-slim` base image. It appears to be missing a required dependency.

Per the Remediation Protocol, I am adding remedial steps to fix this.

## Step 2: Formulate Remedial Tasks

<thinking>
As per my Remediation Ritual, I must first search for remediation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration remediation devops ci/cd failed</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the remediation cases, I will formulate remedial tasks:
1. Fix: Add missing dependencies to Dockerfile (Agent: `aws-devops-engineer`, requires `karen`)
2. Verification: Re-verify the CI pipeline (Agent: `karen`)
</thinking>

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            "Update Infrastructure Files: aws-devops-engineer",
            "Verify Changes: karen",
            "Fix: Add missing CI dependencies: aws-devops-engineer",
            "Re-Verify CI Pipeline: karen"
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

The remedial steps have been added to the plan:
- Step 3 (NEW): Fix the missing dependencies in the Dockerfile
- Step 4 (NEW): Re-verify the CI pipeline build

## Step 5: Proceed with Remediation

<thinking>
I will now delegate the first remedial task back to `aws-devops-engineer`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>aws-devops-engineer</subagent_type>
        <description>Fix missing dependencies in Dockerfile</description>
        <prompt>
<delegate_task>
    <agent_name>aws-devops-engineer</agent_name>
    <task_objective>Fix the `Dockerfile` to include dependencies missing from the new `rust:1.79-slim` base image.</task_objective>
    <requirements>
        - The build failed due to missing `build-essential` and `pkg-config`.
        - You must add a `RUN apt-get update && apt-get install -y build-essential pkg-config` layer to the `Dockerfile`.
        - Ensure this layer is placed correctly before the `cargo build` step.
        - Clean up apt cache to keep the image size small.
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I am now waiting for the `aws-devops-engineer` to complete the fix before delegating to `karen` for re-verification.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": [
            'orchestration',
            'remediation',
            'karen',
            'incomplete',
            'aws-devops-engineer',
            'cicd',
            'docker',
            'build-failure',
            'cbr-retrieval',
            'ritual',
        ]
    }
]