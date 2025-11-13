"""
Orchestration Remediation Delegation Cases for CBR MCP Server
Examples: Delegating remediation fixes, re-verification delegation, parallel remediation
"""

ORCHESTRATION_REMEDIATION_DELEGATION_CASES = [
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
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
security-auditor returned "FAILED: Critical ReDoS vulnerability found in password regex." Show how to delegate the remediation fix to 31337.
""",
        "solution": """
security-auditor has returned "FAILED" triggering the Remediation Ritual. The remedial tasks have been formulated and added to the plan:
- Step 6 (NEW): Fix ReDoS vulnerability (31337)
- Step 7 (NEW): Verify fix (karen)
- Step 8 (NEW): Re-audit (security-auditor)

I will now delegate the security remediation fix to 31337.

<thinking>
I am executing security remediation delegation. As per the Execution Ritual, I must first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation remediation 31337 security vulnerability</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate the security fix to `31337`, the security specialist.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Fix ReDoS vulnerability in password regex (REMEDIATION)</description>
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

After `31337` completes the fix, I will delegate to `karen` for verification, then back to `security-auditor` for re-audit. I am FORBIDDEN from marking the task complete until security-auditor returns "APPROVED".
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "delegation",
            "remediation",
            "31337",
            "security-auditor",
            "security-specialist",
            "vulnerability",
            "redos",
            "failed",
            "blocking-authority",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
karen returned "INCOMPLETE: The CI pipeline failed to build with the new base image." Show how to delegate the remediation fix to aws-devops-engineer.
""",
        "solution": """
karen has returned "INCOMPLETE" triggering the Remediation Ritual. The remedial tasks have been formulated and added to the plan:
- Step 3 (NEW): Fix missing CI dependencies (aws-devops-engineer)
- Step 4 (NEW): Re-verify CI pipeline (karen)

I will now delegate the infrastructure remediation fix to aws-devops-engineer.

<thinking>
I am executing infrastructure remediation delegation. As per the Execution Ritual, I must first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation remediation aws-devops-engineer infrastructure</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate the infrastructure fix to `aws-devops-engineer`.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>aws-devops-engineer</subagent_type>
        <description>Fix missing dependencies in Dockerfile (REMEDIATION)</description>
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

After the `aws-devops-engineer` completes this fix, I will delegate to `karen` for re-verification of the CI pipeline.
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "delegation",
            "remediation",
            "aws-devops-engineer",
            "karen",
            "incomplete",
            "infrastructure",
            "cicd",
            "docker",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After parallel remediation fixes are complete, show how to delegate re-verification to karen, then re-review to code-reviewer.
""",
        "solution": """
Both remediation tracks (UI fixes and Backend fix) are now complete. I must now delegate re-verification and re-review.

Current status:
- Step 6 (UI Fixes): ui-developer - COMPLETED
- Step 8 (Backend Fix): firebase-backend-architect - COMPLETED
- Step 9 (Verify All Fixes): karen - PENDING
- Step 10 (Re-Review Code): code-reviewer - PENDING

I will now delegate to karen for comprehensive re-verification.

<thinking>
I am delegating the re-verification step. As per the Execution Ritual, I must first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen verification remediation</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` for comprehensive verification of all fixes.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify all remediation fixes</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify that all remediation fixes from code-reviewer are working correctly.</task_objective>
    <requirements>
        You must verify ALL of these fixes:

        1. UI: Network error handling is now present and functional
        2. UI: Naming conventions are now consistent throughout
        3. Backend: Token validation is now implemented and secure

        Run all relevant tests and manually verify functionality where needed.

        RESPOND WITH:
        - "VERIFIED COMPLETE" if all fixes are working
        - "INCOMPLETE: [specific issue]" if any fixes are insufficient
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After `karen` returns "VERIFIED COMPLETE", I will then delegate to `code-reviewer` for final re-review. I am FORBIDDEN from marking the task complete until code-reviewer returns "APPROVED".
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "delegation",
            "remediation",
            "karen",
            "verification",
            "re-verification",
            "join-phase",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After karen verifies all remediation fixes, show how to delegate final re-review to code-reviewer (blocking authority).
""",
        "solution": """
karen has returned "VERIFIED COMPLETE" for all remediation fixes. I must now delegate to code-reviewer for final re-review.

Current status:
- Step 6 (UI Fixes): ui-developer - COMPLETED
- Step 8 (Backend Fix): firebase-backend-architect - COMPLETED
- Step 9 (Verify All Fixes): karen - COMPLETED
- Step 10 (Re-Review Code): code-reviewer - PENDING

I will now delegate to code-reviewer for blocking authority approval.

<thinking>
I am delegating the final re-review to a BLOCKING AUTHORITY. As per the Execution Ritual, I must first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation code-reviewer blocking-authority re-review</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to `code-reviewer` for final re-review after all remediation fixes are verified.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>code-reviewer</subagent_type>
        <description>Re-review code after remediation fixes</description>
        <prompt>
<delegate_task>
    <agent_name>code-reviewer</agent_name>
    <task_objective>Re-review the Google Sign-In implementation after all remediation fixes have been completed.</task_objective>
    <requirements>
        You previously identified 3 critical issues. All have been fixed and verified by karen:
        
        1. UI: Network error handling has been added
        2. UI: Naming conventions have been corrected
        3. Backend: Token validation has been implemented

        Review all code changes to verify:
        - All previous issues are fully resolved
        - No new issues were introduced during remediation
        - Code quality standards are met
        - Best practices are followed

        RESPOND WITH:
        - "APPROVED" if all issues are resolved
        - "FAILED: [issues]" if problems remain
    </requirements>
    <critical>You are a BLOCKING AUTHORITY. The task cannot be marked complete until you respond with "APPROVED". Respond with "FAILED" if critical issues remain.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for the `code-reviewer`'s response. I am FORBIDDEN from marking the task complete until this agent provides "APPROVED" status.
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "delegation",
            "remediation",
            "code-reviewer",
            "blocking-authority",
            "re-review",
            "finalization",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After 31337 completes security fix, show how to delegate re-verification to karen, then re-audit to security-auditor.
""",
        "solution": """
The security specialist 31337 has completed the ReDoS vulnerability fix. I must now delegate re-verification and re-audit.

Current status:
- Step 6 (Fix ReDoS): 31337 - COMPLETED
- Step 7 (Verify Fix): karen - PENDING
- Step 8 (Re-Audit): security-auditor - PENDING

I will now delegate to karen for verification of the security fix.

<thinking>
I am delegating security fix verification. As per the Execution Ritual, I must first search `cbr-retrieval` for relevant examples.
</thinking>

<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration delegation karen verification security fix</query>
        <category>orchestration</category>
        <subcategory>remediation</subcategory>
    </tool>
</tool_code>

<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` for verification of the security fix.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify ReDoS vulnerability fix</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify that the ReDoS vulnerability in the password strength regex has been fixed.</task_objective>
    <requirements>
        31337 has rewritten the password strength regex to eliminate the ReDoS vulnerability.
        
        You must verify:
        - The new regex still enforces all password strength requirements
        - The ReDoS vulnerability tests now pass
        - All existing password validation tests still pass
        - The regex performs efficiently even with pathological inputs

        Run all tests in the test suite related to password validation.

        RESPOND WITH:
        - "VERIFIED COMPLETE" if the fix is working correctly
        - "INCOMPLETE: [specific issue]" if the fix is insufficient
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After `karen` returns "VERIFIED COMPLETE", I will then delegate to `security-auditor` for the final blocking re-audit. I am FORBIDDEN from marking the task complete until security-auditor returns "APPROVED".
""",
        "category": "orchestration",
        "subcategory": "remediation",
        "tags": [
            "orchestration",
            "delegation",
            "remediation",
            "karen",
            "31337",
            "security",
            "verification",
            "vulnerability-fix",
            "cbr-retrieval",
        ],
    },
]