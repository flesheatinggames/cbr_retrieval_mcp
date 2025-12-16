"""
Orchestration Remediation Cases for CBR MCP Server
Examples: Handling verification failures and executing the Remediation Ritual
"""

ORCHESTRATION_REMEDIATION_CASES = [
    {
        "problem": """
karen returned "INCOMPLETE: The button lacks a proper loading state." Show how to delegate the remediation fix to ui-developer.
""",
        "solution": """
Karen has returned "INCOMPLETE" triggering the Remediation Ritual. The remedial tasks have been formulated and added to the plan:
- Step 3 (NEW): Fix loading state (ui-developer)
- Step 4 (NEW): Re-verify (karen)

I will now delegate the remediation fix to the ui-developer.

<thinking>
I am executing the remediation delegation. As per the Execution Ritual, I must first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation remediation ui-developer fix</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate the remedial fix to `ui-developer`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Add loading state to GoogleSignInButton (REMEDIATION)</description>
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

After the `ui-developer` completes this fix, I will delegate to `karen` for re-verification. I am FORBIDDEN from marking the task complete until karen returns "VERIFIED COMPLETE".
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "delegation",
            "remediation",
            "ui-developer",
            "karen",
            "incomplete",
            "verification-failure",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
code-reviewer returned "FAILED: Found 3 critical issues" (2 UI issues, 1 backend issue). Show how to delegate the parallel remediation fixes.
""",
        "solution": """
code-reviewer has returned "FAILED" triggering the Remediation Ritual. The remedial tasks have been formulated and added to the plan:

*Track A (UI):*
- Step 6 (NEW): Fix network error handling and naming (ui-developer)

*Track B (Backend):*
- Step 8 (NEW): Fix token validation (firebase-backend-architect)

*Join Phase:*
- Step 9 (NEW): Verify all fixes (karen)
- Step 10 (NEW): Re-review code (code-reviewer)

I will now delegate the remediation fixes in parallel.

<thinking>
I have two parallel remediation tracks to delegate. As per the Execution Ritual, I must first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation remediation parallel code-reviewer</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate both remediation tracks in parallel - UI fixes to `ui-developer` and backend fix to `firebase-backend-architect`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Fix code review UI issues (REMEDIATION)</description>
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
        <description>Fix code review backend issue (REMEDIATION)</description>
        <prompt>
<delegate_task>
    <agent_name>firebase-backend-architect</agent_name>
    <task_objective>Fix the critical backend issue identified by code-reviewer.</task_objective>
    <requirements>
        Critical issue to fix:

        1. Token not validated before use
           - Add token signature verification before processing
           - Add token expiration check
           - Handle invalid tokens gracefully and return a proper error response

        - Maintain all existing functionality
        - Ensure all tests still pass
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After both tracks complete, I will delegate to `karen` for verification, then back to `code-reviewer` for re-review. I am FORBIDDEN from marking the task complete until code-reviewer returns "APPROVED".
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "delegation",
            "remediation",
            "code-reviewer",
            "parallel",
            "ui-developer",
            "firebase-backend-architect",
            "failed",
            "blocking-authority",
            "karen",
            "verification",
            "workflow",
            "agents",
        ],
    },
]