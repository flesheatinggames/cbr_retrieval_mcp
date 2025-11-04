"""
Orchestration Delegation Cases for CBR MCP Server
Examples: Proper delegation format, multi-agent coordination, task delegation, workflow handoffs
"""

ORCHESTRATION_DELEGATION_CASES = [
    {
        "problem": """
User: "I need to add Google Sign-In to our application."

The orchestrator has created a plan. Now show how to properly delegate the first task to the ui-developer.
""",
        "solution": """
The approved plan has these steps:
1. Create GoogleSignInButton component (ui-developer + karen)
2. Create handleGoogleAuthToken function (firebase-backend-architect + karen)
3. Code review (code-reviewer)

I will now delegate the first task to the ui-developer using the proper delegation format:

<tool_code>
    <tool name="Task">
        <subagent_type>ui-developer</subagent_type>
        <description>Create GoogleSignInButton component</description>
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

After the ui-developer completes this work, I will delegate to karen for verification before proceeding to the next step in the plan.
""",
        "category": "orchestration",
        "subcategory": "delegation",
        "tags": [
            "orchestration",
            "delegation",
            "ui-developer",
            "task-tool",
            "proper-format",
            "google-auth",
        ],
    }
]
