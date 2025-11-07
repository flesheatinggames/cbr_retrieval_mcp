"""
Orchestration Planning Cases for CBR MCP Server
Examples: Proper Orchestration Ritual, two-phase planning, internal checkpoints, parallelization, cbr-retrieval
"""

ORCHESTRATION_PLANNING_CASES = [
    {
        "problem": """
User: "I need to add Google Sign-In to our application."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning Google Sign-In</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task, looking for parallel execution opportunities.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** Decomposing "Google Sign-In" into verifiable units of work that can run in parallel.

*Track A (UI):*
1. UI Work: Create the `GoogleSignInButton` component. (Agent: `ui-developer`, requires `karen`). This is one component.
2. Verification: Verify the `GoogleSignInButton` component. (Agent: `karen`).

*Track B (Backend):*
3. Backend Work: Create the `handleGoogleAuthToken` function. (Agent: `firebase-backend-architect`, requires `karen`). This is one function.
4. Verification: Verify the `handleGoogleAuthToken` function. (Agent: `karen`).

**Finalization Phase (Joins Tracks):**
5. Code Review: Review all new code from both tracks. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Create UI Component: ui-developer",
    "Verify UI Component: karen",
    "Create Backend Function: firebase-backend-architect",
    "Verify Backend Function: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - Plan is decomposed into a single component and a single function. This passes the litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `requires-karen` agents (ui-developer, firebase-backend-architect) have a `karen` step. PASS.
- CHECK 3: PARALLELIZATION - UI work (1-2) and Backend work (3-4) are correctly identified to run in parallel. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - The plan includes the mandatory `code-reviewer`. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - UI work → ui-developer, Backend work → firebase-backend-architect, Final review → code-reviewer. PASS.
- CHECK 6: SYNCHRONIZATION - Todos match the 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

I have created a complete plan for my specialist agents. Here it is:

## Implementation Plan for Google Sign-In

**Implementation Phase (Parallel Tracks):**

*Track A (UI):*
1. **Create UI Component** - **Agent: ui-developer** - Create the `GoogleSignInButton` React component.
2. **Verify UI Component** - **Agent: karen** - Verify the new UI component renders correctly.

*Track B (Backend):*
3. **Create Backend Function** - **Agent: firebase-backend-architect** - Create the `handleGoogleAuthToken` Cloud Function.
4. **Verify Backend Function** - **Agent: karen** - Verify the backend authentication logic is working.

**Finalization Phase:**
5. **Final Code Review** - **Agent: code-reviewer** - Review all new code after implementation and verification.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "ritual",
            "checkpoint",
            "two-phase",
            "google-auth",
            "firebase",
            "parallel",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Add a last_login_ip field to the User model in the database."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning database migration field</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Decomposing database field addition into verifiable units:

1. Write Migration Tests: Test that the repository can handle the new `last_login_ip` field. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Model/Repository Change: Add the field to the `User` struct and update the repository logic. (Agent: `rust-developer`, requires `karen`). This is one model change.
4. Verification: Verify the model implementation. (Agent: `karen`).
5. Write Migration Script: Create the database migration script to add the new column. (Agent: `aws-devops-engineer`, requires `karen`). This is one migration script.
6. Verification: Verify migration script syntax and safety. (Agent: `karen`).

**Finalization Phase:**
7. Code Review: Review all code changes. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Repository Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Update Code: rust-developer",
    "Verify Code: karen",
    "Write Migration Script: aws-devops-engineer",
    "Verify Migration Script: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one model change, one migration script. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer, rust-developer, and aws-devops-engineer all have karen verification. PASS.
- CHECK 3: PARALLELIZATION - The steps (TDD, Implementation, Migration) are sequential and cannot be parallelized. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Rust code → rust-developer, Infrastructure → aws-devops-engineer. PASS.
- CHECK 6: SYNCHRONIZATION - 7 todos match 7-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Adding `last_login_ip` Field

**Implementation Phase:**
1. **Write Repository Tests** - **Agent: tdd-test-engineer** - Test the data access layer for the new field.
2. **Verify Tests** - **Agent: karen** - Verify the tests are correct.
3. **Update Code** - **Agent: rust-developer** - Update the application code to add the field.
4. **Verify Code** - **Agent: karen** - Verify the code changes.
5. **Write Migration Script** - **Agent: aws-devops-engineer** - Create the DB migration script.
6. **Verify Migration Script** - **Agent: karen** - Verify the script syntax and safety.

**Finalization Phase:**
7. **Final Code Review** - **Agent: code-reviewer** - Review all changes.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "database",
            "migration",
            "tdd",
            "rust",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "The /api/v1/analytics/report endpoint is too slow. Find the bottleneck and optimize it."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning performance investigation debugging</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, this requires an investigation phase before a full implementation plan can be made.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Investigation Phase:** The user is reporting a performance issue with an unknown cause. The first step is investigation.

1. Debug Performance: Use the `debug-specialist` to analyze the endpoint, find the performance bottleneck (e.g., N+1 query, slow computation), and recommend a fix. (Agent: `debug-specialist`).

The fix will require a new plan after the investigation is complete.
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Investigate Bottleneck: debug-specialist"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One investigation task. This is appropriate since we need information before we can plan fixes. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - debug-specialist does not require karen. PASS.
- CHECK 3: PARALLELIZATION - Not applicable for a single-step investigation plan. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Not applicable for investigation phase; will be included in follow-up plan. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Unknown bug cause → debug-specialist per agent directory. PASS.
- CHECK 6: SYNCHRONIZATION - 1 todo matches 1-step investigation plan and is in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Plan for Performance Investigation

1. **Investigate Bottleneck** - **Agent: debug-specialist** - Analyze the slow endpoint and provide a root cause analysis with a recommended solution.

Once the analysis is complete, I will formulate a new plan to implement the fix.

Do you approve this investigation plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "investigation",
            "debugging",
            "performance",
            "two-phase",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Add internationalization support for French to the <UserProfile> component."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning internationalization i18n</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Decomposing i18n work into verifiable units:

1. Create Translation Files: Add the necessary French (fr) translation files for all text in the `<UserProfile>` component. (Agent: `i18n-specialist`, requires `karen`). This is one translation file set.
2. Verification: Verify files exist and have correct keys. (Agent: `karen`).
3. Implement i18n in Component: Refactor the `<UserProfile>` component to use the i18n library to display the translated text. (Agent: `ui-developer`, requires `karen`). This is one component refactor.
4. Verification: Verify component renders correctly with French text. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review all i18n changes. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Create Translations: i18n-specialist",
    "Verify Translations: karen",
    "Implement in Component: ui-developer",
    "Verify Implementation: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One translation file set, one component refactor. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - i18n-specialist and ui-developer both have karen verification. PASS.
- CHECK 3: PARALLELIZATION - The steps (Create files, Implement in component) are sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - i18n work → i18n-specialist, UI refactor → ui-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Internationalization

**Implementation Phase:**
1. **Create Translations** - **Agent: i18n-specialist** - Add French translation files.
2. **Verify Translations** - **Agent: karen** - Check the new files.
3. **Implement in Component** - **Agent: ui-developer** - Update the component to use the translations.
4. **Verify Implementation** - **Agent: karen** - Confirm the component renders correctly.

**Finalization Phase:**
5. **Final Code Review** - **Agent: code-reviewer** - Review all i18n changes.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "i18n",
            "internationalization",
            "ui",
            "react",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Add a dark mode toggle to the UI that persists the user's preference."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning full-stack dark mode</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task, looking for parallel execution opportunities.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** Full-stack feature involving UI, state management, and backend. These tracks can be developed in parallel.

*Track A (Backend):*
1. Backend TDD: Write tests for a new endpoint `/api/user/preferences` that accepts a theme preference. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Backend Implementation: Implement the endpoint to save the user's preference to the database. (Agent: `firebase-backend-architect`, requires `karen`). This is one endpoint.
4. Verification: Verify the endpoint. (Agent: `karen`).

*Track B (UI Component):*
5. Frontend TDD UI: Write tests for a new `<ThemeToggle>` component. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
6. Verification: Verify the tests. (Agent: `karen`).
7. Frontend UI Implementation: Build the `<ThemeToggle>` component. (Agent: `ui-developer`, requires `karen`). This is one component.
8. Verification: Verify the component. (Agent: `karen`).

*Track C (Client Logic):*
9. Frontend TDD Logic: Write tests for the client-side logic that calls the backend and applies the theme. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
10. Verification: Verify the tests. (Agent: `karen`).
11. Frontend Logic Implementation: Implement the logic to manage the theme state and call the API. (Agent: `ui-developer`, requires `karen`). This is one logic module.
12. Verification: Verify the logic. (Agent: `karen`).

**Finalization Phase (Joins Tracks):**
13. Code Review: Review all frontend and backend code. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Backend API Tests: tdd-test-engineer",
    "Verify API Tests: karen",
    "Backend API Implementation: firebase-backend-architect",
    "Verify API Implementation: karen",
    "Frontend UI Tests: tdd-test-engineer",
    "Verify UI Tests: karen",
    "Frontend UI Implementation: ui-developer",
    "Verify UI Implementation: karen",
    "Frontend Logic Tests: tdd-test-engineer",
    "Verify Logic Tests: karen",
    "Frontend Logic Implementation: ui-developer",
    "Verify Logic Implementation: karen",
    "Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One endpoint, one component, one logic module, each with their test suite. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All requires-karen agents have karen verification steps. PASS.
- CHECK 3: PARALLELIZATION - Backend (1-4), UI (5-8), and Client Logic (9-12) are correctly identified as parallel tracks. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Backend → firebase-backend-architect, UI → ui-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 13 todos match 13-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Dark Mode Feature

**Implementation Phase (Parallel Tracks):**

*Track A (Backend):*
1. **Backend API Tests** - **Agent: tdd-test-engineer** - Write tests for preferences endpoint.
2. **Verify API Tests** - **Agent: karen** - Verify the tests.
3. **Backend API Implementation** - **Agent: firebase-backend-architect** - Implement the endpoint.
4. **Verify API Implementation** - **Agent: karen** - Verify the endpoint.

*Track B (UI Component):*
5. **Frontend UI Tests** - **Agent: tdd-test-engineer** - Write tests for `<ThemeToggle>`.
6. **Verify UI Tests** - **Agent: karen** - Verify the tests.
7. **Frontend UI Implementation** - **Agent: ui-developer** - Build the component.
8. **Verify UI Implementation** - **Agent: karen** - Verify the component.

*Track C (Client Logic):*
9. **Frontend Logic Tests** - **Agent: tdd-test-engineer** - Write tests for theme management.
10. **Verify Logic Tests** - **Agent: karen** - Verify the tests.
11. **Frontend Logic Implementation** - **Agent: ui-developer** - Implement the logic.
12. **Verify Logic Implementation** - **Agent: karen** - Verify the logic.

**Finalization Phase:**
13. **Code Review** - **Agent: code-reviewer** - Review all code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "full-stack",
            "ui",
            "backend",
            "tdd",
            "firebase",
            "parallel",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Analyze the project's requirements from the PRD and create a task breakdown."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning PRD analysis product-strategist</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, this is a planning delegation task for the product-strategist.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Planning Delegation:** The user is asking for a planning operation based on a Product Requirements Document (PRD). According to the agent directory, complex planning work must be delegated to the `product-strategist`.

1. Parse PRD and Create Plan: Delegate the entire planning process to the `product-strategist`. (Agent: `product-strategist`, requires `karen`). This is one planning document.
2. Verification: Verify that the plan aligns with the PRD. (Agent: `karen`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Delegate Planning: product-strategist",
    "Verify Plan: karen"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One planning document. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - product-strategist requires karen, and karen step is included. PASS.
- CHECK 3: PARALLELIZATION - Steps are sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Not applicable for planning delegation; product-strategist produces the plan itself. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - PRD analysis and planning → product-strategist per agent directory. PASS.
- CHECK 6: SYNCHRONIZATION - 2 todos match 2-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Plan for Project Task Breakdown

1. **Delegate Planning** - **Agent: product-strategist** - Analyze the PRD and create the project plan.
2. **Verify Plan** - **Agent: karen** - Verify the completeness and accuracy of the generated plan.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "delegation",
            "product-strategy",
            "prd",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Refactor the PaymentProcessor service to use the new StripeClient instead of the legacy BraintreeClient."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning refactor tdd</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Decomposing refactoring work into verifiable units:

1. Write Refactoring Tests: Ensure existing tests cover all legacy client behavior. Write new tests for the StripeClient if needed. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Refactor: Swap the BraintreeClient with the new StripeClient. (Agent: `rust-developer`, requires `karen`). This is one service refactor.
4. Verification: Verify all tests pass. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review the refactored code. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Implement Refactor: rust-developer",
    "Verify Implementation: karen",
    "Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one service refactor. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Rust refactor → rust-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for PaymentProcessor Refactor

**Implementation Phase:**
1. **Write Tests** - **Agent: tdd-test-engineer** - Create tests ensuring the new `StripeClient` behaves as expected.
2. **Verify Tests** - **Agent: karen** - Confirm test quality and coverage.
3. **Implement Refactor** - **Agent: rust-developer** - Perform the refactoring.
4. **Verify Implementation** - **Agent: karen** - Ensure all tests pass.

**Finalization Phase:**
5. **Code Review** - **Agent: code-reviewer** - Final quality check.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "refactoring",
            "tdd",
            "rust",
            "payment",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Integrate with the WeatherAPI to fetch the current weather for a user's location."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning api integration client</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Decomposing API integration into verifiable units:

1. Write WeatherAPI Client Tests: Create tests for a new service that will call the WeatherAPI. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement WeatherAPI Client: Build the client. (Agent: `rust-developer`, requires `karen`). This is one client.
4. Verification: Verify the client. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review the new client code. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Client Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Implement Client: rust-developer",
    "Verify Implementation: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one client. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Rust client → rust-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for WeatherAPI Integration

**Implementation Phase:**
1. **Write Client Tests** - **Agent: tdd-test-engineer** - Create tests for the new API client.
2. **Verify Tests** - **Agent: karen** - Verify the tests.
3. **Implement Client** - **Agent: rust-developer** - Build the client.
4. **Verify Implementation** - **Agent: karen** - Verify the implementation.

**Finalization Phase:**
5. **Final Code Review** - **Agent: code-reviewer** - Review all code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "api-integration",
            "tdd",
            "rust",
            "weather",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Implement a feature flag for the new 'AI Summary' feature."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning feature flag tdd</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Decomposing feature flag implementation into verifiable units:

1. TDD for Flag Logic: Write tests for the service that will check if the 'AI Summary' feature flag is enabled. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Flag Check: Implement the logic. (Agent: `rust-developer`, requires `karen`). This is one logic module.
4. Verification: Verify the logic. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review the implementation. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Implement Logic: rust-developer",
    "Verify Implementation: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one logic module. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Logic → rust-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Feature Flag Implementation

**Implementation Phase:**
1. **Write Tests** - **Agent: tdd-test-engineer** - Create tests for the flag logic.
2. **Verify Tests** - **Agent: karen** - Verify the tests.
3. **Implement Logic** - **Agent: rust-developer** - Add the feature flag check.
4. **Verify Implementation** - **Agent: karen** - Verify the implementation.

**Finalization Phase:**
5. **Final Code Review** - **Agent: code-reviewer** - Review all code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "feature-flags",
            "tdd",
            "rust",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Scaffold a new microservice for handling user notifications."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning scaffold microservice devops</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Scaffolding a new service from a template is a DevOps task.

1. Scaffold Service: Use the company's microservice template to create the basic project structure for the `notifications-service`. (Agent: `aws-devops-engineer`, requires `karen`). This is one service scaffold.
2. Verification: Verify the project builds and default tests pass. (Agent: `karen`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Scaffold Service: aws-devops-engineer",
    "Verify: karen"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One service scaffold. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - aws-devops-engineer has karen verification. PASS.
- CHECK 3: PARALLELIZATION - Steps are sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Not applicable for scaffolding; no code to review yet. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Infrastructure/scaffolding → aws-devops-engineer. PASS.
- CHECK 6: SYNCHRONIZATION - 2 todos match 2-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Plan for New Microservice

1. **Scaffold Service** - **Agent: aws-devops-engineer** - Create the new service from the project template.
2. **Verify** - **Agent: karen** - Ensure the newly created service is valid and buildable.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "scaffolding",
            "microservices",
            "devops",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Update the Dockerfile and CI/CD pipeline to use the new base image rust:1.79-slim."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning docker ci/cd devops</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** This is a pure DevOps and infrastructure change.

1. Update Files: Modify the `Dockerfile` and `.github/workflows/ci.yml` to use the new base image. (Agent: `aws-devops-engineer`, requires `karen`). This is one configuration change.
2. Verification: Verify the CI pipeline completes successfully with the new image. (Agent: `karen`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Update Infrastructure Files: aws-devops-engineer",
    "Verify Changes: karen"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One configuration change. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - aws-devops-engineer has karen verification. PASS.
- CHECK 3: PARALLELIZATION - Steps are sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Not applicable for infrastructure changes. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Docker/CI configuration → aws-devops-engineer. PASS.
- CHECK 6: SYNCHRONIZATION - 2 todos match 2-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Plan for CI/CD Update

1. **Update Infrastructure Files** - **Agent: aws-devops-engineer** - Update the necessary configuration files.
2. **Verify Changes** - **Agent: karen** - Trigger and verify the CI pipeline to confirm the change is working.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "docker",
            "cicd",
            "devops",
            "rust",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Remove the deprecated LegacyReporting module and all its usages."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning deprecation removal refactor</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Removing code requires careful testing to ensure no regressions.

1. Write Tests: Write characterization tests around the code that uses the `LegacyReporting` module to lock down its current behavior. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Remove Module: Delete the `LegacyReporting` module and refactor the code that used it. (Agent: `rust-developer`, requires `karen`). This is one module deletion.
4. Verification: Ensure all tests still pass. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review the removal. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Remove Code: rust-developer",
    "Verify Removal: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one module deletion. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Code removal → rust-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Deprecation Removal

**Implementation Phase:**
1. **Write Tests** - **Agent: tdd-test-engineer** - Write tests to prevent regressions.
2. **Verify Tests** - **Agent: karen** - Verify the tests.
3. **Remove Code** - **Agent: rust-developer** - Perform the code removal and refactoring.
4. **Verify Removal** - **Agent: karen** - Run all tests and confirm success.

**Finalization Phase:**
5. **Final Code Review** - **Agent: code-reviewer** - Review all changes.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "deprecation",
            "refactoring",
            "tdd",
            "rust",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Fix the accessibility issues on the login form. It is missing labels and has poor color contrast."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning accessibility a11y</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** This is a UI and accessibility (a11y) task.

1. Fix A11y Issues: Update the login form component to add proper `aria-labels` and adjust the CSS to meet WCAG color contrast standards. (Agent: `ui-developer`, requires `karen`). This is one component update.
2. Verification: Run an automated accessibility checker like Axe and verify the specific issues are resolved. (Agent: `karen`).

**Finalization Phase:**
3. Code Review: Review the accessibility improvements. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Implement Fixes: ui-developer",
    "Verify Fixes: karen",
    "Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One component update. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - ui-developer has karen verification. PASS.
- CHECK 3: PARALLELIZATION - Steps are sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - UI/accessibility → ui-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 3 todos match 3-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Accessibility Fixes

**Implementation Phase:**
1. **Implement Fixes** - **Agent: ui-developer** - Update the login form's code and styles.
2. **Verify Fixes** - **Agent: karen** - Run accessibility checks and confirm the issues are resolved.

**Finalization Phase:**
3. **Code Review** - **Agent: code-reviewer** - Review all changes.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "accessibility",
            "ui",
            "a11y",
            "wcag",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Add structured logging to the authentication service."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning logging tdd</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Adding logging statements at key points in the authentication flow.

1. TDD for Logging: Write tests that mock the logger and assert that it's called with the correct structured data on login success and failure. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Logging: Add the logging statements to the authentication service code. (Agent: `rust-developer`, requires `karen`). This is one service update.
4. Verification: Verify the logging implementation. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review the implementation. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Implement Logging: rust-developer",
    "Verify Implementation: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one service update. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Logging → rust-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Structured Logging

**Implementation Phase:**
1. **Write Tests** - **Agent: tdd-test-engineer** - Create tests that verify logging output.
2. **Verify Tests** - **Agent: karen** - Verify the tests.
3. **Implement Logging** - **Agent: rust-developer** - Add the logging code.
4. **Verify Implementation** - **Agent: karen** - Confirm tests pass.

**Finalization Phase:**
5. **Final Code Review** - **Agent: code-reviewer** - Review all changes.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "logging",
            "authentication",
            "tdd",
            "rust",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Create a nightly cron job that cleans up expired user sessions from the database."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning cron job devops</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task, looking for parallel execution opportunities.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** This requires two distinct parts that can be done in parallel: the cleanup logic and the scheduling mechanism.

*Track A (Logic):*
1. TDD for Cleanup Logic: Write tests for the function that will delete expired sessions. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Cleanup Logic: Write the session cleanup function. (Agent: `rust-developer`, requires `karen`). This is one function.
4. Verification: Verify the function. (Agent: `karen`).

*Track B (Infrastructure):*
5. Schedule Cron Job: Create the infrastructure configuration (e.g., a Kubernetes CronJob YAML or an AWS Lambda scheduled event) to run the cleanup logic nightly. (Agent: `aws-devops-engineer`, requires `karen`). This is one cron configuration.
6. Verification: Verify the job is scheduled in the target environment. (Agent: `karen`).

**Finalization Phase (Joins Tracks):**
7. Code Review: Review the cleanup logic code (from Track A). (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Logic Tests: tdd-test-engineer",
    "Verify Logic Tests: karen",
    "Implement Logic: rust-developer",
    "Verify Logic: karen",
    "Schedule Job: aws-devops-engineer",
    "Verify Schedule: karen",
    "Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one function, one cron configuration. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All three agents have karen verification. PASS.
- CHECK 3: PARALLELIZATION - Cleanup Logic (1-4) and Cron Scheduling (5-6) are correctly identified as parallel tracks. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Function → rust-developer, Cron → aws-devops-engineer. PASS.
- CHECK 6: SYNCHRONIZATION - 7 todos match 7-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Session Cleanup Cron Job

**Implementation Phase (Parallel Tracks):**

*Track A (Logic):*
1. **Write Logic Tests** - **Agent: tdd-test-engineer** - Test the cleanup logic.
2. **Verify Logic Tests** - **Agent: karen** - Verify the tests.
3. **Implement Logic** - **Agent: rust-developer** - Write the cleanup function.
4. **Verify Logic** - **Agent: karen** - Verify the function.

*Track B (Infrastructure):*
5. **Schedule Job** - **Agent: aws-devops-engineer** - Set up the cron job infrastructure.
6. **Verify Schedule** - **Agent: karen** - Verify scheduling.

**Finalization Phase:**
7. **Code Review** - **Agent: code-reviewer** - Review the cleanup code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "cron",
            "scheduling",
            "database",
            "cleanup",
            "tdd",
            "parallel",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Add server-side validation to the user registration endpoint for password strength."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning validation security tdd</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** This is a classic TDD case for modifying an existing endpoint.

1. Write Failing Tests: Add new tests to the registration endpoint test suite that assert a 400 Bad Request is returned for weak passwords. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite addition.
2. Verification: Verify the new tests fail as expected. (Agent: `karen`).
3. Implement Validation: Add the password validation logic to the registration endpoint handler. (Agent: `rust-developer`, requires `karen`). This is one validation addition.
4. Verification: Verify all tests, including the new ones, now pass. (Agent: `karen`).

**Finalization Phase:**
5. Security Audit: Since this touches authentication, a security review is required. (Agent: `security-auditor`, blocking authority).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Failing Tests: tdd-test-engineer",
    "Verify Failing Tests: karen",
    "Implement Validation: rust-developer",
    "Verify Implementation: karen",
    "Security Audit: security-auditor"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite addition, one validation addition. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - security-auditor included (blocking authority for auth changes). PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Validation → rust-developer, Security → security-auditor. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Password Validation

**Implementation Phase:**
1. **Write Failing Tests** - **Agent: tdd-test-engineer** - Add tests for the new validation rules.
2. **Verify Failing Tests** - **Agent: karen** - Confirm the tests fail as expected.
3. **Implement Validation** - **Agent: rust-developer** - Add the server-side logic.
4. **Verify Implementation** - **Agent: karen** - Confirm all tests now pass.

**Finalization Phase:**
5. **Security Audit** - **Agent: security-auditor** - Final security review.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "validation",
            "security",
            "authentication",
            "tdd",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Implement a Redis caching layer for the get_product_list function."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning caching redis tdd</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Modifying an existing function to add caching logic.

1. TDD for Caching: Write tests for the `get_product_list` function that cover cache hit and cache miss scenarios. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Caching: Modify the function to include logic to check Redis for cached data before hitting the database. (Agent: `rust-developer`, requires `karen`). This is one function modification.
4. Verification: Verify the function. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review the implementation. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Implement Caching: rust-developer",
    "Verify Implementation: karen",
    "Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test suite, one function modification. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Caching → rust-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Caching Layer

**Implementation Phase:**
1. **Write Tests** - **Agent: tdd-test-engineer** - Test cache hit/miss scenarios.
2. **Verify Tests** - **Agent: karen** - Verify the tests.
3. **Implement Caching** - **Agent: rust-developer** - Add the Redis logic.
4. **Verify Implementation** - **Agent: karen** - Verify the implementation.

**Finalization Phase:**
5. **Code Review** - **Agent: code-reviewer** - Review all code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "caching",
            "redis",
            "performance",
            "tdd",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Create a new GET endpoint /api/v1/health that returns a 200 OK."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning health check endpoint</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Very simple, standard backend task. The full TDD workflow should still be followed for consistency.

1. Write Tests: Create a test file for the health endpoint that asserts a 200 status code and expected JSON body. (Agent: `tdd-test-engineer`, requires `karen`). This is one test file.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Endpoint: Create the route and handler for `/api/v1/health`. (Agent: `rust-developer`, requires `karen`). This is one endpoint.
4. Verification: Verify the endpoint. (Agent: `karen`).

**Finalization Phase:**
5. Code Review: Review the code. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Write Tests: tdd-test-engineer",
    "Verify Tests: karen",
    "Implement Endpoint: rust-developer",
    "Verify Implementation: karen",
    "Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One test file, one endpoint. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - tdd-test-engineer and rust-developer have karen verification. PASS.
- CHECK 3: PARALLELIZATION - TDD workflow is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, Endpoint → rust-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 5 todos match 5-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Health Endpoint

**Implementation Phase:**
1. **Write Tests** - **Agent: tdd-test-engineer** - Create tests for the endpoint.
2. **Verify Tests** - **Agent: karen** - Verify the tests.
3. **Implement Endpoint** - **Agent: rust-developer** - Create the route and handler.
4. **Verify Implementation** - **Agent: karen** - Verify the endpoint.

**Finalization Phase:**
5. **Code Review** - **Agent: code-reviewer** - Review all code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "api",
            "health-check",
            "tdd",
            "rust",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Migrate the state management in the Dashboard page from local state to a global Zustand store."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning state management zustand</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases, I will now decompose the task.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase:** Frontend refactoring task broken into creating the store and using the store.

1. TDD for Zustand Store: Write tests for the new global dashboard store, covering its actions and initial state. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Zustand Store: Create the Zustand store file. (Agent: `ui-developer`, requires `karen`). This is one store file.
4. Verification: Verify the store. (Agent: `karen`).
5. TDD for Component Refactor: Write tests for the Dashboard page that mock the new store and assert correct rendering. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
6. Verification: Verify the tests. (Agent: `karen`).
7. Implement Component Refactor: Refactor the Dashboard component to use the new store instead of local state. (Agent: `ui-developer`, requires `karen`). This is one component refactor.
8. Verification: Verify the refactor. (Agent: `karen`).

**Finalization Phase:**
9. Code Review: Review all changes. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Test Store: tdd-test-engineer",
    "Verify Store Tests: karen",
    "Implement Store: ui-developer",
    "Verify Store: karen",
    "Test Component: tdd-test-engineer",
    "Verify Component Tests: karen",
    "Implement Component Refactor: ui-developer",
    "Verify Component Refactor: karen",
    "Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One store file, one component refactor, each with test suites. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All requires-karen agents have karen verification. PASS.
- CHECK 3: PARALLELIZATION - Store creation (1-4) must precede component refactoring (5-8). The plan is sequential. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - code-reviewer included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Tests → tdd-test-engineer, UI → ui-developer. PASS.
- CHECK 6: SYNCHRONIZATION - 9 todos match 9-step plan and are in the correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for State Management Migration

**Implementation Phase:**
1. **Test Store** - **Agent: tdd-test-engineer** - Test the new store.
2. **Verify Store Tests** - **Agent: karen** - Verify the tests.
3. **Implement Store** - **Agent: ui-developer** - Create the store.
4. **Verify Store** - **Agent: karen** - Verify the store.
5. **Test Component** - **Agent: tdd-test-engineer** - Test the refactored component.
6. **Verify Component Tests** - **Agent: karen** - Verify the tests.
7. **Implement Component Refactor** - **Agent: ui-developer** - Refactor the component.
8. **Verify Component Refactor** - **Agent: karen** - Verify the refactor.

**Finalization Phase:**
9. **Code Review** - **Agent: code-reviewer** - Review all changes.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "state-management",
            "zustand",
            "react",
            "ui",
            "tdd",
            "cbr-retrieval",
        ],
    },
]