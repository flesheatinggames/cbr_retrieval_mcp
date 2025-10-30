"""
Orchestration Remediation Cases for CBR MCP Server
Examples: Handling failed verification, remediation workflow after karen feedback
"""

ORCHESTRATION_REMEDIATION_CASES = [
    {
        "problem": "The ui-developer completed the GoogleSignInButton component, but karen's verification returned 'INCOMPLETE: The button lacks a proper loading state.' How do I handle this failed verification and implement the remediation workflow?",
        "solution": """
<thinking>
`karen` has returned "INCOMPLETE". I MUST now execute the Remediation Protocol.
1. Acknowledge the deviation to the user.
2. Create new todos for the remedial work: one for the fix, one for re-verification.
3. Use `TodoWrite` to ADD these new todos to the existing list, without altering the
original approved todos which are the Plan of Record.
</thinking>

I have an update: `karen` has reviewed the `GoogleSignInButton` and found an issue. The
button is missing a loading state. Per my protocol, I am adding the following remedial steps
to our plan:

1a. **Add Loading State** - **Agent: ui-developer** - Add a loading indicator
to the `GoogleSignInButton` component.
1b. **Re-verify UI Component** - **Agent: karen** -
Re-verify the component after the fix.

I will now delegate the first remedial task to the `ui-developer`.

<TodoWrite>
[
    {"content": "Delegate to ui-developer to create GoogleSignInButton component", "status": "completed"},
    {"content": "Delegate to karen to verify UI component", "status": "completed"},
    {"content": "Delegate to ui-developer to add loading state to GoogleSignInButton component", "status": "pending", "activeForm": "Delegating to ui-developer to add loading state"},
    {"content": "Delegate to karen to re-verify UI component after loading state fix", "status": "pending", "activeForm": "Delegating to karen to re-verify component"},
    {"content": "Delegate to firebase-backend-architect to create handleGoogleAuthToken function", "status": "pending"},
    {"content": "Delegate to karen to verify backend function", "status": "pending"},
    {"content": "Delegate to code-reviewer for final review", "status": "pending"}
]
</TodoWrite>

**Key Remediation Protocol Steps:**

1. **Automatic Triggers** - When ANY BLOCKING AUTHORITY agent (karen, code-reviewer, security-auditor) responds with these keywords, remediation is AUTOMATICALLY required:
   - "FAILED" → IMMEDIATE remediation protocol activation
   - "INCOMPLETE" → Task remains in progress, completion FORBIDDEN
   - "REJECTED" → IMMEDIATE remediation protocol activation
   - "CRITICAL ISSUES" → IMMEDIATE remediation protocol activation

2. **Announce the Deviation** - Inform the user that a verification failed and what the issue is.

3. **Formulate Remedial Tasks** - Create a new, granular list of tasks required to fix the issue. This usually involves a "fix" step and a "re-verify" step.

4. **Append, Do Not Replace** - Use the `TodoWrite` tool to **ADD** these new remedial tasks to the existing todo list.
   - The new tasks should be inserted immediately after the failed step.
   - You MUST NOT alter any of the original, approved todos from the Plan of Record.

5. **Announce the New Plan** - Inform the user of the new steps you have added to the plan.

6. **Proceed** - Delegate the first new remedial task.

**Completion Blocking:**
While remediation is pending:
- You are FORBIDDEN from declaring task completion
- You CANNOT summarize work as "complete"
- You MUST focus exclusively on addressing blocking issues
- NO completion-related language until remediation resolves all blocking issues

**Example Remediation Workflow:**

Original Plan:
1. Delegate to ui-developer → COMPLETED
2. Delegate to karen → INCOMPLETE (issue found)
3. Delegate to backend-architect → PENDING
4. Delegate to karen → PENDING
5. Delegate to code-reviewer → PENDING

After Remediation Protocol:
1. Delegate to ui-developer → COMPLETED
2. Delegate to karen → COMPLETED (with issues)
3. **Delegate to ui-developer (FIX)** → PENDING (NEW REMEDIAL TASK)
4. **Delegate to karen (RE-VERIFY)** → PENDING (NEW REMEDIAL TASK)
5. Delegate to backend-architect → PENDING (original plan continues)
6. Delegate to karen → PENDING
7. Delegate to code-reviewer → PENDING

The Plan of Record is preserved, and remedial tasks are inserted to address the issue before continuing with the original workflow.
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "remediation",
            "verification",
            "failure",
            "recovery",
            "karen",
            "incomplete",
            "workflow",
            "agents",
            "orchestration",
            "blocking-authority",
            "delegation",
            "plan-of-record",
            "protocol",
            "ui-developer",
            "verification-failure",
            "fix-and-reverify",
            "append-tasks",
            "execution-ritual"
        ]
    },
    {
        "problem": "The security audit found we need to add HTTP Security Headers like CSP and HSTS.",
        "solution": """
<sequential-thinking>
This is a security hardening task that involves middleware changes.

1.  **Implement Security Headers:** Add middleware to the web server that injects Content-Security-Policy (CSP), Strict-Transport-Security (HSTS), and other recommended security headers into all responses.
    -   Agent: 31337 (security specialist)
    -   Verification: karen (verify headers are present in server responses)
2.  **Security Audit:** Have the changes formally audited.
    -   Agent: security-auditor (blocking authority)

This is a 3-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to 31337 to implement middleware for adding HTTP security headers",
        "status": "pending",
        "activeForm": "Delegating to 31337 to implement headers"
    },
    {
        "content": "Delegate to karen to verify the security headers are present on HTTP responses",
        "status": "pending",
        "activeForm": "Delegating to karen to verify headers"
    },
    {
        "content": "Delegate to security-auditor to re-audit the application for HTTP security headers",
        "status": "pending",
        "activeForm": "Delegating to security-auditor for re-audit"
    }
]
</TodoWrite>

## Plan for HTTP Security Headers

1.  **Implement Headers:** Delegate to **31337** to add the required middleware.
2.  **Verify Implementation:** Delegate to **karen** to check that responses now include the correct headers.
3.  **Security Audit:** Delegate to **security-auditor** for a final verification of the security posture.

Do you approve this plan?
"""
    }
]
