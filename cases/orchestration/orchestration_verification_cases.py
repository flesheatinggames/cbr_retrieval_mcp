"""
Orchestration Verification Cases for CBR MCP Server
Examples: Delegating to karen for verification, parallel verification, TDD verification, infrastructure verification
"""

ORCHESTRATION_VERIFICATION_CASES = [
    {
        "problem": """
After ui-developer completes the GoogleSignInButton component, show how to properly delegate to karen for verification following the Execution Ritual.
""",
        "solution": """
The ui-developer has reported that the GoogleSignInButton component is complete.

According to the Execution Ritual (Step 2: Verify) and my agent directory, ui-developer is a requires-karen agent. I MUST delegate to karen for verification before proceeding.

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
I have reviewed the delegation examples. I will now delegate to `karen` for verification of the UI component, following the verification protocol.
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

**Verification Workflow:**

I will wait for karen's response following the verification protocol:

1. **If karen returns "VERIFIED COMPLETE"**:
   - I will immediately execute the Task Completion Protocol
   - Update the subtask status in tasks.md
   - Check if all subtasks are complete before marking parent task complete
   - Proceed to the next pending subtask or task

2. **If karen returns "INCOMPLETE: [issue]"**:
   - I will immediately trigger the Remediation Ritual
   - Create new remedial tasks to fix the specific issues
   - Append these new tasks to TodoWrite (never modify the Plan of Record)
   - Delegate the first remedial task
   - Re-verify with karen after fixes are complete

**Key Verification Principles:**

- **Blocking Authority**: karen's response blocks my progress until resolved
- **No Self-Verification**: I NEVER verify my own work or skip karen for requires-karen agents
- **Binary Response**: Only "VERIFIED COMPLETE" or "INCOMPLETE" - no "mostly done"
- **Immediate Action**: Execute Task Completion Protocol immediately upon VERIFIED COMPLETE
- **Mandatory Re-verification**: After remediation, always re-verify with karen

**Common Verification Patterns:**

- **TDD Red Phase**: karen verifies new tests fail correctly before implementation
- **TDD Green Phase**: karen verifies all tests pass after implementation
- **Parallel Verification**: delegate multiple verification tasks to karen simultaneously
- **Infrastructure Verification**: karen triggers and monitors actual CI/CD pipelines
- **Security Verification**: karen validates security fixes with actual security tests
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "verification",
            "karen",
            "delegation",
            "execution-ritual",
            "requires-karen",
            "blocking-authority",
            "quality-check",
            "testing",
            "validation",
            "cbr-retrieval",
        ],
    },
]