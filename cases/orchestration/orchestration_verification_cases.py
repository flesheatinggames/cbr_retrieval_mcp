"""
Orchestration Verification Cases for CBR MCP Server
Examples: Karen verification patterns, quality checking, validation workflows, parallel verification, TDD verification, DevOps verification
"""

ORCHESTRATION_VERIFICATION_CASES = [
    {
        "problem": """
After ui-developer completes the GoogleSignInButton component, show how to properly delegate to karen for verification.
""",
        "solution": """
The ui-developer has reported that the GoogleSignInButton component is complete.

According to the Execution Ritual and my agent directory, ui-developer is a requires-karen agent. I MUST delegate to karen for verification before proceeding.

<thinking>
As per my Execution Ritual (Step 1: Delegate), I must first search for verification delegation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration verification delegation karen ui-developer</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory> 
    </tool>
</tool_code>
<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` for verification.
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
            "cbr-retrieval",
            "ritual",
        ],
    },
    {
        "problem": """
The `ui-developer` and `firebase-backend-architect` have both completed their parallel tasks for the Google Sign-In feature. Show how to delegate for parallel verification.
""",
        "solution": """
The `ui-developer` (Track A) and `firebase-backend-architect` (Track B) have both reported completion.

My plan requires verification for both. I can delegate these two verification tasks to `karen` in parallel.

<thinking>
As per my Execution Ritual (Step 1: Delegate), I must first search for verification delegation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration verification parallel delegation</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory> 
    </tool>
</tool_code>
<thinking>
I have reviewed the delegation examples. I will now delegate *both* verification tasks to `karen` in parallel.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify GoogleSignInButton component (Track A)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the GoogleSignInButton component (Track A) implementation.</task_objective>
    <requirements>
The ui-developer has completed the GoogleSignInButton component.

## File to verify
src/components/auth/GoogleSignInButton.tsx

## Verification criteria
- **Functionality**: Component initiates OAuth flow.
- **Loading State**: Component displays loading indicator.
- **Error Handling**: Component handles error states.
- **Styling**: Component uses Bootstrap classes.
    </requirements>
    <critical>Respond with "VERIFIED COMPLETE" or "INCOMPLETE" with details.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify handleGoogleAuthToken function (Track B)</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the `handleGoogleAuthToken` function (Track B) implementation.</task_objective>
    <requirements>
The firebase-backend-architect has completed the `handleGoogleAuthToken` function.

## File to verify
functions/src/auth.ts

## Verification criteria
- **Functionality**: Function correctly processes a test token.
- **Firestore**: Function creates/updates a user record in Firestore.
- **Return Value**: Function returns a custom auth token.
- **Error Handling**: Function handles invalid or expired tokens.
    </requirements>
    <critical>Respond with "VERIFIED COMPLETE" or "INCOMPLETE" with details.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will now wait for `karen` to return a status for *both* tasks before proceeding with the join phase (Code Review).
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "verification",
            "karen",
            "parallel",
            "ui-developer",
            "firebase-backend-architect",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After `tdd-test-engineer` completes writing the *failing tests* for the `last_login_ip` feature, show how to delegate to `karen` to verify them.
""",
        "solution": """
The `tdd-test-engineer` has reported that the new tests for `last_login_ip` are complete.

The TDD process requires that these new tests *fail* before implementation begins. I must delegate to `karen` to verify this specific "failing" requirement.

<thinking>
As per my Execution Ritual (Step 1: Delegate), I must first search for verification delegation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration verification tdd failing tests</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory> 
    </tool>
</tool_code>
<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` to verify the failing tests.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify failing tests for last_login_ip</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the new tests for `last_login_ip` fail as expected.</task_objective>
    <requirements>
The `tdd-test-engineer` has added new tests for a field that does not exist yet.

## File to verify
`tests/test_user_repository.rs`

## Verification criteria
1. **Run Tests**: Execute the test suite for `test_user_repository`.
2. **Confirm Failure**: Verify that the *new* tests related to `last_login_ip` FAIL.
3. **Confirm No Regressions**: Verify that all *existing* tests in the suite still PASS.

## Response format

If VERIFIED COMPLETE (tests fail as expected):
- State "VERIFIED COMPLETE"
- Confirm "New tests failed as expected. Existing tests passed."

If INCOMPLETE (new tests pass, or existing tests fail):
- State "INCOMPLETE"
- Report which tests failed or passed incorrectly.
    </requirements>
    <critical>This is a TDD verification. The new tests MUST fail for this step to be complete.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `karen`'s response. If "VERIFIED COMPLETE" (meaning the tests failed correctly), I will proceed to the implementation step.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "verification",
            "karen",
            "tdd-test-engineer",
            "tdd",
            "failing-tests",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
After `aws-devops-engineer` updates the CI/CD pipeline to use a new base image, show how to delegate to `karen` for verification.
""",
        "solution": """
The `aws-devops-engineer` has reported that the `Dockerfile` and `ci.yml` have been updated.

I must now delegate to `karen` to verify that the pipeline still builds correctly *before* this code is merged.

<thinking>
As per my Execution Ritual (Step 1: Delegate), I must first search for verification delegation examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration verification devops ci-cd docker</query>
        <category>orchestration</category>
        <subcategory>delegation</subcategory> 
    </tool>
</tool_code>
<thinking>
I have reviewed the delegation examples. I will now delegate to `karen` to verify the CI pipeline.
</thinking>

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify CI pipeline build with new base image</description>
        <prompt>
<delegate_task>
    <agent_name>karen</agent_name>
    <task_objective>Verify the CI pipeline passes after changes to the `Dockerfile` and `ci.yml`.</task_objective>
    <requirements>
The `aws-devops-engineer` has updated the base image to `rust:1.79-slim`.

## Files to verify
- `Dockerfile`
- `.github/workflows/ci.yml`

## Verification criteria
1. **Trigger Build**: Trigger a new build of the CI pipeline.
2. **Confirm Success**: Verify that all stages of the pipeline (build, test, lint) complete successfully.
3. **Check Logs**: Check the build logs to confirm the new base image `rust:1.79-slim` was pulled and used.

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Confirm "CI pipeline passed successfully with the new base image."

If INCOMPLETE:
- State "INCOMPLETE"
- Provide the error log from the failed pipeline step.
    </requirements>
    <critical>You must trigger and monitor the actual CI pipeline for verification.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

I will wait for `karen`'s response. If the pipeline fails ("INCOMPLETE"), I will trigger the Remediation Ritual.
""",
        "category": "orchestration",
        "subcategory": "verification",
        "tags": [
            "orchestration",
            "verification",
            "karen",
            "aws-devops-engineer",
            "devops",
            "ci-cd",
            "docker",
            "cbr-retrieval",
        ],
    }
]