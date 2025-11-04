"""
Orchestration Verification Cases for CBR MCP Server
Examples: Karen verification patterns, quality checking, validation workflows
"""

ORCHESTRATION_VERIFICATION_CASES = [
    {
        "problem": """
After ui-developer completes the GoogleSignInButton component, show how to properly delegate to karen for verification.
""",
        "solution": """
The ui-developer has reported that the GoogleSignInButton component is complete.

According to the Execution Ritual and my agent directory, ui-developer is a requires-karen agent. I MUST delegate to karen for verification before proceeding.

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

Please verify this work meets all requirements:

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
- State "INCOMPLETE"
- List specific issues that need to be fixed
- Be detailed enough that the ui-developer can address the issues
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before proceeding. If karen returns "VERIFIED COMPLETE", I will mark the task as complete and proceed to the next step. If karen returns "INCOMPLETE", I will execute the Remediation Protocol.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "verification",
            "karen",
            "ui-developer",
            "requires-karen",
            "component",
        ],
    }
]
