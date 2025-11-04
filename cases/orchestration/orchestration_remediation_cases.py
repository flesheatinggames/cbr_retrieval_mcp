"""
Orchestration Remediation Cases for CBR MCP Server
Examples: Handling failed verification, remediation workflow, recovery protocols
"""

ORCHESTRATION_REMEDIATION_CASES = [
    {
        "problem": """
karen returned "INCOMPLETE: The button lacks a proper loading state." Show how to execute the Remediation Protocol.
""",
        "solution": """
Karen has returned "INCOMPLETE" which is a MANDATORY REMEDIATION TRIGGER.

I MUST now execute the Remediation Protocol:

## Step 1: Announce the Deviation

I have an update: karen has reviewed the GoogleSignInButton and found an issue. The button is missing a loading state during authentication. Per the Remediation Protocol, I am adding remedial steps to address this issue.

## Step 2: Formulate Remedial Tasks

I need to:
1. Delegate back to ui-developer to add the loading state
2. Delegate to karen to re-verify after the fix

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            {"content": "Delegate to ui-developer to create GoogleSignInButton component", "status": "completed", "activeForm": "Delegating to ui-developer to create button component"},
            {"content": "Delegate to karen to verify UI component", "status": "completed", "activeForm": "Delegating to karen to verify UI component"},
            {"content": "Delegate to ui-developer to add loading state to GoogleSignInButton", "status": "pending", "activeForm": "Delegating to ui-developer to fix loading state"},
            {"content": "Delegate to karen to re-verify UI component", "status": "pending", "activeForm": "Delegating to karen to re-verify UI component"},
            {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "pending", "activeForm": "Delegating to firebase-backend-architect to create auth function"},
            {"content": "Delegate to karen to verify backend function", "status": "pending", "activeForm": "Delegating to karen to verify backend function"},
            {"content": "Delegate to code-reviewer for final review", "status": "pending", "activeForm": "Delegating to code-reviewer for final review"}
        ]
    </tool>
</tool_code>

CRITICAL: I have NOT altered the original approved todos from the Plan of Record. I have ADDED new remedial tasks (steps 3 and 4) immediately after the failed step.

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
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "remediation",
            "karen",
            "incomplete",
            "ui",
            "verification-failure",
            "workflow",
            "agents",
        ],
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

1. Missing error handling for network failures
2. Token not validated before use
3. Inconsistent naming conventions

Per the Remediation Protocol, I am adding remedial steps to fix these issues.

## Step 2: Formulate Remedial Tasks

I need to:
1. Delegate to appropriate developer to fix the critical issues
2. Delegate to karen to verify the fixes
3. Delegate to code-reviewer to re-review

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            {"content": "Delegate to ui-developer to create GoogleSignInButton component", "status": "completed", "activeForm": "Delegating to ui-developer to create button component"},
            {"content": "Delegate to karen to verify UI component", "status": "completed", "activeForm": "Delegating to karen to verify UI component"},
            {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "completed", "activeForm": "Delegating to firebase-backend-architect to create auth function"},
            {"content": "Delegate to karen to verify backend function", "status": "completed", "activeForm": "Delegating to karen to verify backend function"},
            {"content": "Delegate to code-reviewer for final review", "status": "completed", "activeForm": "Delegating to code-reviewer for final review"},
            {"content": "Delegate to ui-developer to fix critical issues found in code review", "status": "pending", "activeForm": "Delegating to ui-developer to fix code review issues"},
            {"content": "Delegate to karen to verify code review fixes", "status": "pending", "activeForm": "Delegating to karen to verify fixes"},
            {"content": "Delegate to code-reviewer to re-review after fixes", "status": "pending", "activeForm": "Delegating to code-reviewer for re-review"}
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

The remedial steps have been added to the plan:
- Step 6 (NEW): Fix the 3 critical issues
- Step 7 (NEW): Verify the fixes
- Step 8 (NEW): Re-review the code

## Step 5: Proceed with Remediation

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Fix code review critical issues</description>
        <prompt>
<delegate_task>
    <agent_name>ui-developer</agent_name>
    <task_objective>Fix the 3 critical issues identified by code-reviewer in the Google Sign-In implementation</task_objective>
    <requirements>
        Critical issues to fix:

        1. Missing error handling for network failures
           - Add try-catch blocks for network requests
           - Display user-friendly error messages
           - Implement retry logic for transient failures

        2. Token not validated before use
           - Add token validation before passing to backend
           - Check token format and expiration
           - Handle invalid tokens gracefully

        3. Inconsistent naming conventions
           - Rename variables/functions to follow project conventions
           - Update all references consistently
           - Ensure naming is clear and descriptive

        - Maintain all existing functionality
        - Ensure all tests still pass
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for ui-developer to complete the fixes, then delegate to karen for verification, then back to code-reviewer for re-review.
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "remediation",
            "code-reviewer",
            "failed",
            "blocking-authority",
            "critical-issues",
            "workflow",
            "agents",
        ],
    },
]
