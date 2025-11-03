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
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": ['orchestration', 'remediation', 'karen', 'incomplete', 'ui', 'verification-failure']
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
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": ['orchestration', 'remediation', 'code-reviewer', 'failed', 'blocking-authority', 'critical-issues']
    },
    {
        "problem": """
security-auditor returned "FAILED: CRITICAL vulnerability - JWT tokens not validated for expiration." Show the Remediation Protocol for security failures.
""",
        "solution": """
security-auditor has returned "FAILED" which is a MANDATORY REMEDIATION TRIGGER.

security-auditor is a BLOCKING AUTHORITY. This is a CRITICAL security vulnerability that MUST be fixed immediately.

## Step 1: Announce the Deviation

I have an update: security-auditor has identified a CRITICAL security vulnerability. JWT tokens are not being validated for expiration, which could allow attackers to use expired tokens. Per the Remediation Protocol, I am adding remedial steps to fix this vulnerability immediately.

## Step 2: Formulate Remedial Tasks

I need to:
1. Delegate to 31337 (security specialist) to fix the vulnerability
2. Delegate to karen to verify the fix
3. Delegate to security-auditor to re-audit

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "completed", "activeForm": "Delegating to firebase-backend-architect to create auth function"},
            {"content": "Delegate to karen to verify backend function", "status": "completed", "activeForm": "Delegating to karen to verify backend function"},
            {"content": "Delegate to code-reviewer for final review", "status": "completed", "activeForm": "Delegating to code-reviewer for final review"},
            {"content": "Delegate to security-auditor to audit authentication", "status": "completed", "activeForm": "Delegating to security-auditor for audit"},
            {"content": "Delegate to 31337 to fix CRITICAL JWT expiration vulnerability", "status": "pending", "activeForm": "Delegating to 31337 to fix security vulnerability"},
            {"content": "Delegate to karen to verify security fix", "status": "pending", "activeForm": "Delegating to karen to verify fix"},
            {"content": "Delegate to security-auditor to re-audit after fix", "status": "pending", "activeForm": "Delegating to security-auditor for re-audit"}
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

CRITICAL SECURITY ISSUE requires immediate remediation:
- Step 5 (NEW): Fix JWT expiration validation vulnerability
- Step 6 (NEW): Verify the security fix
- Step 7 (NEW): Re-audit to confirm vulnerability is resolved

## Step 5: Proceed with Remediation

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Fix JWT expiration vulnerability</description>
        <prompt>
<delegate_task>
    <agent_name>31337</agent_name>
    <task_objective>Fix the CRITICAL security vulnerability where JWT tokens are not validated for expiration</task_objective>
    <requirements>
        CRITICAL SECURITY FIX:

        - Implement proper JWT expiration validation
        - Check token expiration timestamp before accepting the token
        - Reject expired tokens with 401 Unauthorized response
        - Include appropriate error message: "Token expired"
        - Ensure validation happens before any business logic execution
        - Add unit tests for expired token scenarios
        - Verify fix prevents replay attacks with old tokens
        - Follow OWASP JWT security best practices
        - Maintain all existing functionality
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for 31337 to fix the vulnerability, then delegate to karen for verification, then back to security-auditor for re-audit to confirm the vulnerability is resolved.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": ['orchestration', 'remediation', 'security-auditor', 'failed', 'critical', 'security', '31337', 'jwt']
    },
    {
        "problem": """
karen returned "INCOMPLETE" for the second time after a fix was applied. Show how to handle multiple failed verifications in sequence.
""",
        "solution": """
Karen has returned "INCOMPLETE" AGAIN after the first remedial fix was applied.

This is the SECOND failed verification. I MUST execute the Remediation Protocol again.

## Current State

Original plan:
1. Create GoogleSignInButton - COMPLETED
2. Verify component - COMPLETED (INCOMPLETE - missing loading state)
3. Fix loading state - COMPLETED
4. Re-verify component - COMPLETED (INCOMPLETE AGAIN - loading state not accessible)
5. Backend work - PENDING
6. Final review - PENDING

## Step 1: Announce the Deviation

I have another update: karen has re-verified the GoogleSignInButton after the loading state fix, but found a new issue. The loading state is not accessible - it's missing the aria-busy attribute. Per the Remediation Protocol, I am adding additional remedial steps.

## Step 2: Formulate Remedial Tasks

I need to:
1. Delegate to ui-developer to add accessibility attributes
2. Delegate to karen to re-verify (third verification attempt)

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            {"content": "Delegate to ui-developer to create GoogleSignInButton component", "status": "completed", "activeForm": "Delegating to ui-developer to create button component"},
            {"content": "Delegate to karen to verify UI component", "status": "completed", "activeForm": "Delegating to karen to verify UI component"},
            {"content": "Delegate to ui-developer to add loading state to GoogleSignInButton", "status": "completed", "activeForm": "Delegating to ui-developer to fix loading state"},
            {"content": "Delegate to karen to re-verify UI component", "status": "completed", "activeForm": "Delegating to karen to re-verify UI component"},
            {"content": "Delegate to ui-developer to add accessibility attributes to loading state", "status": "pending", "activeForm": "Delegating to ui-developer to add a11y attributes"},
            {"content": "Delegate to karen to re-verify UI component accessibility", "status": "pending", "activeForm": "Delegating to karen for third verification"},
            {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "pending", "activeForm": "Delegating to firebase-backend-architect to create auth function"},
            {"content": "Delegate to karen to verify backend function", "status": "pending", "activeForm": "Delegating to karen to verify backend function"},
            {"content": "Delegate to code-reviewer for final review", "status": "pending", "activeForm": "Delegating to code-reviewer for final review"}
        ]
    </tool>
</tool_code>

IMPORTANT: This is the SECOND remediation iteration. The Plan of Record continues to grow as we address each issue found by karen. All original approved steps remain in the list.

## Step 4: Announce the New Plan

Additional remedial steps have been added:
- Step 5 (NEW): Add accessibility attributes to loading state
- Step 6 (NEW): Third verification attempt

## Step 5: Proceed with Remediation

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Add accessibility to loading state</description>
        <prompt>
<delegate_task>
    <agent_name>ui-developer</agent_name>
    <task_objective>Add proper accessibility attributes to the loading state in GoogleSignInButton component</task_objective>
    <requirements>
        - Add aria-busy="true" attribute when loading is true
        - Add aria-busy="false" when loading is false
        - Ensure screen readers announce the loading state change
        - Add aria-label="Signing in with Google, please wait" when loading
        - Maintain all existing functionality
        - Verify with automated accessibility checker (axe or similar)
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

This is an example of iterative remediation - addressing issues as they are discovered through successive verification attempts.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": ['orchestration', 'remediation', 'karen', 'multiple-failures', 'iterative', 'accessibility']
    },
    {
        "problem": """
After fixing security issues, the security-auditor still returns "FAILED" but with different issues. Show how to handle changing remediation requirements.
""",
        "solution": """
security-auditor has returned "FAILED" AGAIN, but this time with DIFFERENT security issues.

This demonstrates that remediation can reveal new issues or that fixes can introduce new problems.

## Current State

Previous security-auditor findings (FIXED):
- CRITICAL: JWT tokens not validated for expiration ✓

New security-auditor findings:
- HIGH: JWT secret key hardcoded in source code
- MEDIUM: Missing rate limiting on token endpoint

## Step 1: Announce the Deviation

I have an update: After fixing the JWT expiration issue, security-auditor has re-audited the code and found 2 additional security issues:
1. HIGH: JWT secret key is hardcoded (should use environment variable)
2. MEDIUM: No rate limiting on the token endpoint (enables brute force)

Per the Remediation Protocol, I am adding remedial steps to address these new issues.

## Step 2: Formulate Remedial Tasks

I need to:
1. Delegate to 31337 to fix both security issues
2. Delegate to karen to verify the fixes
3. Delegate to security-auditor to re-audit (third audit)

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "completed", "activeForm": "Delegating to firebase-backend-architect to create auth function"},
            {"content": "Delegate to karen to verify backend function", "status": "completed", "activeForm": "Delegating to karen to verify backend function"},
            {"content": "Delegate to code-reviewer for final review", "status": "completed", "activeForm": "Delegating to code-reviewer for final review"},
            {"content": "Delegate to security-auditor to audit authentication", "status": "completed", "activeForm": "Delegating to security-auditor for audit"},
            {"content": "Delegate to 31337 to fix CRITICAL JWT expiration vulnerability", "status": "completed", "activeForm": "Delegating to 31337 to fix security vulnerability"},
            {"content": "Delegate to karen to verify security fix", "status": "completed", "activeForm": "Delegating to karen to verify fix"},
            {"content": "Delegate to security-auditor to re-audit after first fix", "status": "completed", "activeForm": "Delegating to security-auditor for re-audit"},
            {"content": "Delegate to 31337 to fix hardcoded JWT secret and add rate limiting", "status": "pending", "activeForm": "Delegating to 31337 to fix additional security issues"},
            {"content": "Delegate to karen to verify second set of security fixes", "status": "pending", "activeForm": "Delegating to karen to verify fixes"},
            {"content": "Delegate to security-auditor for third audit", "status": "pending", "activeForm": "Delegating to security-auditor for final audit"}
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

Additional remedial steps have been added to address new security findings:
- Step 8 (NEW): Fix hardcoded JWT secret and add rate limiting
- Step 9 (NEW): Verify the new fixes
- Step 10 (NEW): Third security audit

## Step 5: Proceed with Remediation

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Fix hardcoded secret and rate limiting</description>
        <prompt>
<delegate_task>
    <agent_name>31337</agent_name>
    <task_objective>Fix two additional security issues found in the authentication implementation</task_objective>
    <requirements>
        Security fixes required:

        1. HIGH: Hardcoded JWT secret key
           - Move JWT secret to environment variable (JWT_SECRET)
           - Remove hardcoded secret from source code
           - Update deployment documentation for environment variable
           - Ensure secret is loaded from environment at runtime
           - Add validation that secret is present on startup

        2. MEDIUM: Missing rate limiting
           - Implement rate limiting on token endpoint
           - Limit: 5 requests per minute per IP address
           - Return 429 Too Many Requests when limit exceeded
           - Include Retry-After header in 429 response
           - Log rate limit violations for monitoring

        - Maintain all existing functionality
        - Ensure previous JWT expiration fix remains in place
        - Add tests for both fixes
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

This demonstrates how security audits can reveal issues iteratively, requiring multiple remediation cycles.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": ['orchestration', 'remediation', 'security-auditor', 'iterative', 'multiple-issues', '31337']
    },
    {
        "problem": """
After remediation work is complete, karen returns "INCOMPLETE" for the remedial fix itself. Show how to handle remediation that needs remediation.
""",
        "solution": """
Karen has returned "INCOMPLETE" for the REMEDIAL FIX ITSELF.

This demonstrates nested remediation - when the fix has its own issues.

## Current State

Original issue: Button missing loading state
First remedial fix: Added loading state
Karen's response: "INCOMPLETE: Loading state implementation has a race condition"

## Step 1: Announce the Deviation

I have an update: karen has verified the loading state fix for the GoogleSignInButton, but found a new issue in the remedial implementation. The loading state has a race condition where rapid clicks can cause multiple authentication attempts. Per the Remediation Protocol, I am adding additional remedial steps to fix the race condition in the loading state logic.

## Step 2: Formulate Remedial Tasks

I need to:
1. Delegate to ui-developer to fix the race condition
2. Delegate to karen to re-verify the loading state implementation

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            {"content": "Delegate to ui-developer to create GoogleSignInButton component", "status": "completed", "activeForm": "Delegating to ui-developer to create button component"},
            {"content": "Delegate to karen to verify UI component", "status": "completed", "activeForm": "Delegating to karen to verify UI component"},
            {"content": "Delegate to ui-developer to add loading state to GoogleSignInButton", "status": "completed", "activeForm": "Delegating to ui-developer to fix loading state"},
            {"content": "Delegate to karen to re-verify UI component", "status": "completed", "activeForm": "Delegating to karen to re-verify UI component"},
            {"content": "Delegate to ui-developer to fix race condition in loading state", "status": "pending", "activeForm": "Delegating to ui-developer to fix race condition"},
            {"content": "Delegate to karen to re-verify loading state after race condition fix", "status": "pending", "activeForm": "Delegating to karen for final verification"},
            {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "pending", "activeForm": "Delegating to firebase-backend-architect to create auth function"},
            {"content": "Delegate to karen to verify backend function", "status": "pending", "activeForm": "Delegating to karen to verify backend function"},
            {"content": "Delegate to code-reviewer for final review", "status": "pending", "activeForm": "Delegating to code-reviewer for final review"}
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

Nested remedial steps have been added:
- Step 5 (NEW): Fix race condition in loading state logic
- Step 6 (NEW): Re-verify the loading state implementation

## Step 5: Proceed with Remediation

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Fix loading state race condition</description>
        <prompt>
<delegate_task>
    <agent_name>ui-developer</agent_name>
    <task_objective>Fix the race condition in the GoogleSignInButton loading state that allows multiple concurrent authentication attempts</task_objective>
    <requirements>
        - Prevent button clicks when loading is true
        - Add disabled attribute to button during loading
        - Ensure only one authentication attempt can be in progress
        - Use proper state management to prevent race conditions
        - Test rapid clicking behavior
        - Ensure existing loading state functionality is preserved
        - Maintain accessibility (aria-busy remains functional)
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

This demonstrates that remediation work itself can have issues requiring additional remediation - nested remediation cycles are normal and expected.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": ['orchestration', 'remediation', 'nested', 'race-condition', 'karen', 'fix-the-fix']
    },
    {
        "problem": """
Multiple agents return blocking failures simultaneously. Show how to handle parallel remediation requirements.
""",
        "solution": """
MULTIPLE BLOCKING AUTHORITIES have returned "FAILED" at the same time.

This demonstrates parallel remediation - when multiple issues must be addressed simultaneously.

## Current State

Blocking failures received:
1. code-reviewer: "FAILED: Missing TypeScript types in 3 files"
2. security-auditor: "FAILED: XSS vulnerability in user input handling"

Both are BLOCKING AUTHORITIES and both MUST be resolved before task completion.

## Step 1: Announce the Deviation

I have an update: Both code-reviewer and security-auditor have identified issues that must be fixed:

**code-reviewer findings:**
- Missing TypeScript types in GoogleSignInButton.tsx
- Missing types in handleGoogleAuthToken.ts
- Missing types in AuthContext.tsx

**security-auditor findings:**
- CRITICAL: XSS vulnerability in user profile display
- Input not sanitized before rendering

Per the Remediation Protocol, I am adding remedial steps to address BOTH sets of issues.

## Step 2: Formulate Remedial Tasks

I need to:
1. Delegate to ui-developer to add missing TypeScript types
2. Delegate to karen to verify types are added
3. Delegate to 31337 to fix XSS vulnerability
4. Delegate to karen to verify security fix
5. Delegate to code-reviewer to re-review
6. Delegate to security-auditor to re-audit

## Step 3: Append to Plan of Record

<tool_code>
    <tool name="TodoWrite">
        [
            {"content": "Delegate to ui-developer to create GoogleSignInButton component", "status": "completed", "activeForm": "Delegating to ui-developer to create button component"},
            {"content": "Delegate to karen to verify UI component", "status": "completed", "activeForm": "Delegating to karen to verify UI component"},
            {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "completed", "activeForm": "Delegating to firebase-backend-architect to create auth function"},
            {"content": "Delegate to karen to verify backend function", "status": "completed", "activeForm": "Delegating to karen to verify backend function"},
            {"content": "Delegate to code-reviewer for final review", "status": "completed", "activeForm": "Delegating to code-reviewer for final review"},
            {"content": "Delegate to security-auditor to audit authentication", "status": "completed", "activeForm": "Delegating to security-auditor for audit"},
            {"content": "Delegate to ui-developer to add missing TypeScript types", "status": "pending", "activeForm": "Delegating to ui-developer to add types"},
            {"content": "Delegate to karen to verify TypeScript types", "status": "pending", "activeForm": "Delegating to karen to verify types"},
            {"content": "Delegate to 31337 to fix XSS vulnerability in user profile", "status": "pending", "activeForm": "Delegating to 31337 to fix XSS"},
            {"content": "Delegate to karen to verify XSS fix", "status": "pending", "activeForm": "Delegating to karen to verify security fix"},
            {"content": "Delegate to code-reviewer for re-review after type fixes", "status": "pending", "activeForm": "Delegating to code-reviewer for re-review"},
            {"content": "Delegate to security-auditor for re-audit after XSS fix", "status": "pending", "activeForm": "Delegating to security-auditor for re-audit"}
        ]
    </tool>
</tool_code>

## Step 4: Announce the New Plan

Parallel remedial steps have been added to address both blocking failures:

**For code-reviewer issues:**
- Step 7 (NEW): Add missing TypeScript types
- Step 8 (NEW): Verify types are added
- Step 11 (NEW): Re-review code

**For security-auditor issues:**
- Step 9 (NEW): Fix XSS vulnerability
- Step 10 (NEW): Verify security fix
- Step 12 (NEW): Re-audit security

## Step 5: Proceed with Remediation (First Issue)

I will address the TypeScript types first, then the security issue:

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Add missing TypeScript types</description>
        <prompt>
<delegate_task>
    <agent_name>ui-developer</agent_name>
    <task_objective>Add proper TypeScript type definitions to all files missing types</task_objective>
    <requirements>
        Files needing type definitions:

        1. GoogleSignInButton.tsx
           - Add proper props interface
           - Add return type to component
           - Add types for all internal state

        2. handleGoogleAuthToken.ts
           - Add types for request parameters
           - Add return type for function
           - Add types for error responses

        3. AuthContext.tsx
           - Add interface for context value
           - Add types for provider props
           - Add types for all state values

        - Ensure strict TypeScript compliance
        - Fix any type errors that emerge
        - Maintain all existing functionality
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After ui-developer completes and karen verifies, I will then delegate the XSS fix to 31337.

This demonstrates handling multiple blocking failures in parallel through sequential remediation of each issue.
""",
        "category": 'orchestration',
        "subcategory": 'remediation',
        "tags": ['orchestration', 'remediation', 'parallel', 'multiple-blockers', 'code-reviewer', 'security-auditor', 'xss', 'typescript']
    }
]
