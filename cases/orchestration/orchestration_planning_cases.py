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
Reviewing the planning cases, I will now decompose the task, looking for parallelization opportunities.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case it is a single component, and the steps (TDD, Implementation, Migration) are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but parallelization is not applicable for a single-step investigation plan. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case it is a single component, and the steps (create translation files, implement translations) are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case it is a single task and verification. The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case the steps must be performed in series (create tests, implement refactor). The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case the steps must be performed in series (create tests, implement client). The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case the steps must be performed in series (create tests, implement feature flag check). The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case it is a single task with verification. The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case it is a single task with verification. The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case the steps must be performed in series (create tests, implement refactor). The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case it is a single task with verification. The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case the steps must be performed in series (create tests, implement logging). The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case the steps must be performed in series (create tests, implement logic). The steps are sequential and cannot be parallelized. PASS.
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
- CHECK 3: PARALLELIZATION - I looked for parallelization opportunities, but in this case the steps must be performed in series (create tests, implement caching logic). The steps are sequential and cannot be parallelized. PASS.
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
    # ========================================================================
    # NEW COMPLEX PARALLEL EXECUTION EXAMPLES (Added for diversity)
    # ========================================================================
    
    {
        "problem": """
User: "Build a complete e-commerce checkout flow with payment processing, order confirmation emails, inventory updates, and analytics tracking."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning e-commerce checkout payment multi-service</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases. This is a complex feature requiring multiple independent services that can be built in parallel: UI, payment backend, email service, inventory service, and analytics.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** Decomposing checkout flow into four independent parallel tracks.

*Track A (Checkout UI):*
1. TDD for Checkout UI: Write tests for checkout form, payment input validation, and order summary. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement Checkout UI: Create the checkout page with form, validation, and order summary. (Agent: `ui-developer`, requires `karen`). This is one page component.
4. Verification: Verify the UI implementation. (Agent: `karen`).

*Track B (Payment & Inventory):*
5. TDD for Payment API: Write tests for payment token validation and transaction processing. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
6. Verification: Verify the tests. (Agent: `karen`).
7. Implement Payment Service: Create the payment processing Cloud Function with Stripe integration. (Agent: `firebase-backend-architect`, requires `karen`). This is one service.
8. Verification: Verify the payment service. (Agent: `karen`).
9. TDD for Inventory: Write tests for inventory decrement and stock validation. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
10. Verification: Verify the tests. (Agent: `karen`).
11. Implement Inventory Service: Create the inventory management with atomic operations. (Agent: `firebase-backend-architect`, requires `karen`). This is one service.
12. Verification: Verify the inventory service. (Agent: `karen`).

*Track C (Notifications):*
13. TDD for Email Service: Write tests for order confirmation email templates and sending logic. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
14. Verification: Verify the tests. (Agent: `karen`).
15. Implement Email Service: Create the email notification Cloud Function. (Agent: `firebase-backend-architect`, requires `karen`). This is one service.
16. Verification: Verify the email service. (Agent: `karen`).

*Track D (Analytics):*
17. TDD for Analytics: Write tests for purchase event tracking. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
18. Verification: Verify the tests. (Agent: `karen`).
19. Implement Analytics Tracking: Add purchase tracking events. (Agent: `firebase-backend-architect`, requires `karen`). This is one tracking module.
20. Verification: Verify analytics. (Agent: `karen`).

**Finalization Phase (Joins All Tracks):**
21. Security Audit: Audit payment handling, PCI compliance, and data protection. (Agent: `security-auditor`).
22. Code Review: Review all code from all tracks for consistency and best practices. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Test Checkout UI: tdd-test-engineer",
    "Verify Checkout UI Tests: karen",
    "Implement Checkout UI: ui-developer",
    "Verify Checkout UI: karen",
    "Test Payment Service: tdd-test-engineer",
    "Verify Payment Tests: karen",
    "Implement Payment Service: firebase-backend-architect",
    "Verify Payment Service: karen",
    "Test Inventory Service: tdd-test-engineer",
    "Verify Inventory Tests: karen",
    "Implement Inventory Service: firebase-backend-architect",
    "Verify Inventory Service: karen",
    "Test Email Service: tdd-test-engineer",
    "Verify Email Tests: karen",
    "Implement Email Service: firebase-backend-architect",
    "Verify Email Service: karen",
    "Test Analytics: tdd-test-engineer",
    "Verify Analytics Tests: karen",
    "Implement Analytics: firebase-backend-architect",
    "Verify Analytics: karen",
    "Security Audit: security-auditor",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One page component, four separate services (payment, inventory, email, analytics). Each is atomic and verifiable. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `requires-karen` agents have `karen` verification steps. PASS.
- CHECK 3: PARALLELIZATION - Four independent tracks (A: 1-4, B: 5-12, C: 13-16, D: 17-20) can run in parallel. Excellent parallelization opportunity. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Both `security-auditor` (required for payment handling) and `code-reviewer` are included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - UI → ui-developer, Backend services → firebase-backend-architect, Tests → tdd-test-engineer, Security → security-auditor. PASS.
- CHECK 6: SYNCHRONIZATION - 22 todos match 22-step plan in correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for E-Commerce Checkout Flow

**Implementation Phase (4 Parallel Tracks):**

*Track A (Checkout UI):*
1. **Test Checkout UI** - **Agent: tdd-test-engineer** - Test the checkout form and validation.
2. **Verify Checkout UI Tests** - **Agent: karen** - Verify the tests.
3. **Implement Checkout UI** - **Agent: ui-developer** - Create the checkout page.
4. **Verify Checkout UI** - **Agent: karen** - Verify the UI.

*Track B (Payment & Inventory):*
5. **Test Payment Service** - **Agent: tdd-test-engineer** - Test payment processing.
6. **Verify Payment Tests** - **Agent: karen** - Verify the tests.
7. **Implement Payment Service** - **Agent: firebase-backend-architect** - Create payment Cloud Function.
8. **Verify Payment Service** - **Agent: karen** - Verify the service.
9. **Test Inventory Service** - **Agent: tdd-test-engineer** - Test inventory updates.
10. **Verify Inventory Tests** - **Agent: karen** - Verify the tests.
11. **Implement Inventory Service** - **Agent: firebase-backend-architect** - Create inventory management.
12. **Verify Inventory Service** - **Agent: karen** - Verify the service.

*Track C (Notifications):*
13. **Test Email Service** - **Agent: tdd-test-engineer** - Test order confirmation emails.
14. **Verify Email Tests** - **Agent: karen** - Verify the tests.
15. **Implement Email Service** - **Agent: firebase-backend-architect** - Create email Cloud Function.
16. **Verify Email Service** - **Agent: karen** - Verify the service.

*Track D (Analytics):*
17. **Test Analytics** - **Agent: tdd-test-engineer** - Test purchase tracking.
18. **Verify Analytics Tests** - **Agent: karen** - Verify the tests.
19. **Implement Analytics** - **Agent: firebase-backend-architect** - Add tracking events.
20. **Verify Analytics** - **Agent: karen** - Verify analytics.

**Finalization Phase:**
21. **Security Audit** - **Agent: security-auditor** - Audit payment security and PCI compliance.
22. **Final Code Review** - **Agent: code-reviewer** - Review all code for consistency.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "e-commerce",
            "payment",
            "multi-service",
            "parallel",
            "4-tracks",
            "security-auditor",
            "complex",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Deploy our microservices application to AWS with infrastructure, monitoring stack, CI/CD pipeline, and documentation."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning AWS deployment infrastructure microservices monitoring</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases. This is a complex deployment with multiple parallel tracks: infrastructure, monitoring setup, CI/CD pipeline, and documentation can all be developed concurrently.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** Decomposing AWS deployment into four independent tracks.

*Track A (Core Infrastructure):*
1. IaC for VPC: Create Terraform for VPC, subnets, security groups, and load balancers. (Agent: `aws-devops-engineer`, requires `karen`). This is one infrastructure module.
2. Verification: Verify the networking infrastructure code. (Agent: `karen`).
3. IaC for ECS Services: Create Terraform for container orchestration, task definitions, and auto-scaling. (Agent: `aws-devops-engineer`, requires `karen`). This is one service module.
4. Verification: Verify the service infrastructure code. (Agent: `karen`).

*Track B (Monitoring Stack):*
5. IaC for CloudWatch: Create monitoring dashboards, alarms, and log groups. (Agent: `aws-devops-engineer`, requires `karen`). This is one monitoring module.
6. Verification: Verify the monitoring configuration. (Agent: `karen`).
7. IaC for X-Ray: Set up distributed tracing across microservices. (Agent: `aws-devops-engineer`, requires `karen`). This is one tracing module.
8. Verification: Verify the tracing configuration. (Agent: `karen`).

*Track C (CI/CD Pipeline):*
9. Pipeline for Build/Test: Create GitHub Actions for automated testing and building. (Agent: `aws-devops-engineer`, requires `karen`). This is one pipeline configuration.
10. Verification: Verify the build pipeline. (Agent: `karen`).
11. Pipeline for Deployment: Create deployment stages with blue-green strategies. (Agent: `aws-devops-engineer`, requires `karen`). This is one deployment configuration.
12. Verification: Verify the deployment pipeline. (Agent: `karen`).

*Track D (Documentation):*
13. Infrastructure Docs: Document the AWS architecture, networking, and deployment process. (Agent: `documentation-specialist`, requires `karen`). This is one documentation set.
14. Verification: Verify documentation completeness. (Agent: `karen`).

**Finalization Phase (Joins All Tracks):**
15. Security Audit: Review IAM policies, encryption, network security, and compliance. (Agent: `security-auditor`).
16. Code Review: Review all IaC and pipeline configurations. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Create VPC Infrastructure: aws-devops-engineer",
    "Verify VPC: karen",
    "Create ECS Services: aws-devops-engineer",
    "Verify ECS: karen",
    "Create CloudWatch Monitoring: aws-devops-engineer",
    "Verify Monitoring: karen",
    "Create X-Ray Tracing: aws-devops-engineer",
    "Verify Tracing: karen",
    "Create Build Pipeline: aws-devops-engineer",
    "Verify Build Pipeline: karen",
    "Create Deployment Pipeline: aws-devops-engineer",
    "Verify Deployment Pipeline: karen",
    "Create Infrastructure Docs: documentation-specialist",
    "Verify Documentation: karen",
    "Security Audit: security-auditor",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - Infrastructure divided into logical modules (networking, services, monitoring, tracing, pipelines, docs). Each is atomic. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `aws-devops-engineer` and `documentation-specialist` tasks have `karen` verification. PASS.
- CHECK 3: PARALLELIZATION - Four independent tracks (A: 1-4, B: 5-8, C: 9-12, D: 13-14) can run in parallel. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Both `security-auditor` and `code-reviewer` included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Infrastructure → aws-devops-engineer, Docs → documentation-specialist, Security → security-auditor. PASS.
- CHECK 6: SYNCHRONIZATION - 16 todos match 16-step plan in correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for AWS Microservices Deployment

**Implementation Phase (4 Parallel Tracks):**

*Track A (Core Infrastructure):*
1. **Create VPC Infrastructure** - **Agent: aws-devops-engineer** - Create networking infrastructure.
2. **Verify VPC** - **Agent: karen** - Verify the infrastructure code.
3. **Create ECS Services** - **Agent: aws-devops-engineer** - Create container orchestration.
4. **Verify ECS** - **Agent: karen** - Verify the service configuration.

*Track B (Monitoring Stack):*
5. **Create CloudWatch Monitoring** - **Agent: aws-devops-engineer** - Set up dashboards and alarms.
6. **Verify Monitoring** - **Agent: karen** - Verify monitoring setup.
7. **Create X-Ray Tracing** - **Agent: aws-devops-engineer** - Set up distributed tracing.
8. **Verify Tracing** - **Agent: karen** - Verify tracing configuration.

*Track C (CI/CD Pipeline):*
9. **Create Build Pipeline** - **Agent: aws-devops-engineer** - Create automated build pipeline.
10. **Verify Build Pipeline** - **Agent: karen** - Verify build configuration.
11. **Create Deployment Pipeline** - **Agent: aws-devops-engineer** - Create deployment automation.
12. **Verify Deployment Pipeline** - **Agent: karen** - Verify deployment configuration.

*Track D (Documentation):*
13. **Create Infrastructure Docs** - **Agent: documentation-specialist** - Document the AWS architecture.
14. **Verify Documentation** - **Agent: karen** - Verify completeness.

**Finalization Phase:**
15. **Security Audit** - **Agent: security-auditor** - Audit IAM, encryption, and network security.
16. **Final Code Review** - **Agent: code-reviewer** - Review all configurations.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "aws",
            "infrastructure",
            "microservices",
            "deployment",
            "monitoring",
            "cicd",
            "parallel",
            "4-tracks",
            "security-auditor",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Build a complete real-time chat feature with WebSocket connections, message persistence, typing indicators, and read receipts."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning real-time chat websocket multi-component</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases. This is a complex feature with multiple parallel components: WebSocket infrastructure, UI components, backend services, and data layer.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** Complex real-time chat with 4 parallel tracks.

*Track A (WebSocket Infrastructure):*
1. TDD for WebSocket Layer: Write tests for connection management, reconnection logic, and heartbeat. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement WebSocket Server: Create WebSocket server with connection pooling and event routing. (Agent: `firebase-backend-architect`, requires `karen`). This is one server implementation.
4. Verification: Verify WebSocket server. (Agent: `karen`).

*Track B (Message Persistence):*
5. TDD for Message Storage: Write tests for message CRUD operations and pagination. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
6. Verification: Verify the tests. (Agent: `karen`).
7. Implement Message Service: Create database schema and API for message persistence. (Agent: `firebase-backend-architect`, requires `karen`). This is one service.
8. Verification: Verify message service. (Agent: `karen`).

*Track C (Real-time Features):*
9. TDD for Typing Indicators: Write tests for typing start/stop events and debouncing. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
10. Verification: Verify the tests. (Agent: `karen`).
11. Implement Typing & Receipts: Create typing indicator and read receipt event handlers. (Agent: `firebase-backend-architect`, requires `karen`). This is one feature module.
12. Verification: Verify real-time features. (Agent: `karen`).

*Track D (Chat UI):*
13. TDD for Chat Components: Write tests for message list, input, and status indicators. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
14. Verification: Verify the tests. (Agent: `karen`).
15. Implement Chat UI: Create chat interface with message bubbles, input, and indicators. (Agent: `ui-developer`, requires `karen`). This is one UI module.
16. Verification: Verify chat UI. (Agent: `karen`).

**Finalization Phase:**
17. Code Review: Review all chat implementation. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Test WebSocket Layer: tdd-test-engineer",
    "Verify WebSocket Tests: karen",
    "Implement WebSocket Server: firebase-backend-architect",
    "Verify WebSocket Server: karen",
    "Test Message Storage: tdd-test-engineer",
    "Verify Storage Tests: karen",
    "Implement Message Service: firebase-backend-architect",
    "Verify Message Service: karen",
    "Test Typing Indicators: tdd-test-engineer",
    "Verify Typing Tests: karen",
    "Implement Typing & Receipts: firebase-backend-architect",
    "Verify Real-time Features: karen",
    "Test Chat UI: tdd-test-engineer",
    "Verify Chat UI Tests: karen",
    "Implement Chat UI: ui-developer",
    "Verify Chat UI: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - Four major components (WebSocket, persistence, real-time features, UI), each atomic. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `requires-karen` agents have karen verification. PASS.
- CHECK 3: PARALLELIZATION - Four independent tracks (A: 1-4, B: 5-8, C: 9-12, D: 13-16) can run in parallel. Excellent parallelization. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - `code-reviewer` included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Backend → firebase-backend-architect, UI → ui-developer, Tests → tdd-test-engineer. PASS.
- CHECK 6: SYNCHRONIZATION - 17 todos match 17-step plan in correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Real-Time Chat Feature

**Implementation Phase (4 Parallel Tracks):**

*Track A (WebSocket Infrastructure):*
1. **Test WebSocket Layer** - **Agent: tdd-test-engineer** - Test connection management.
2. **Verify WebSocket Tests** - **Agent: karen** - Verify the tests.
3. **Implement WebSocket Server** - **Agent: firebase-backend-architect** - Create WebSocket server.
4. **Verify WebSocket Server** - **Agent: karen** - Verify the server.

*Track B (Message Persistence):*
5. **Test Message Storage** - **Agent: tdd-test-engineer** - Test message CRUD.
6. **Verify Storage Tests** - **Agent: karen** - Verify the tests.
7. **Implement Message Service** - **Agent: firebase-backend-architect** - Create message persistence.
8. **Verify Message Service** - **Agent: karen** - Verify the service.

*Track C (Real-time Features):*
9. **Test Typing Indicators** - **Agent: tdd-test-engineer** - Test typing events.
10. **Verify Typing Tests** - **Agent: karen** - Verify the tests.
11. **Implement Typing & Receipts** - **Agent: firebase-backend-architect** - Create real-time features.
12. **Verify Real-time Features** - **Agent: karen** - Verify the features.

*Track D (Chat UI):*
13. **Test Chat UI** - **Agent: tdd-test-engineer** - Test chat components.
14. **Verify Chat UI Tests** - **Agent: karen** - Verify the tests.
15. **Implement Chat UI** - **Agent: ui-developer** - Create chat interface.
16. **Verify Chat UI** - **Agent: karen** - Verify the UI.

**Finalization Phase:**
17. **Final Code Review** - **Agent: code-reviewer** - Review all implementation.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "real-time",
            "chat",
            "websocket",
            "complex",
            "parallel",
            "4-tracks",
            "multi-component",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Add multi-language support to our application for English, Spanish, French, German, and Japanese."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning internationalization i18n multi-language</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases. I18n is an excellent parallelization opportunity - after setting up the infrastructure, each language can be translated independently.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Mixed Sequential and Parallel):** First set up i18n infrastructure, then parallelize translations.

*Phase 1 (Sequential - Infrastructure):*
1. TDD for i18n Setup: Write tests for language detection, switching, and fallback behavior. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement i18n Infrastructure: Set up i18next or similar, configure routing, and create language switcher UI. (Agent: `ui-developer`, requires `karen`). This is one infrastructure setup.
4. Verification: Verify the i18n setup. (Agent: `karen`).

*Phase 2 (Parallel - Translations):*
5. Spanish Translation: Create es.json with all UI strings translated to Spanish. (Agent: `i18n-specialist`, requires `karen`). This is one translation file.
6. Verification: Verify Spanish translations. (Agent: `karen`).
7. French Translation: Create fr.json with all UI strings translated to French. (Agent: `i18n-specialist`, requires `karen`). This is one translation file.
8. Verification: Verify French translations. (Agent: `karen`).
9. German Translation: Create de.json with all UI strings translated to German. (Agent: `i18n-specialist`, requires `karen`). This is one translation file.
10. Verification: Verify German translations. (Agent: `karen`).
11. Japanese Translation: Create ja.json with all UI strings translated to Japanese. (Agent: `i18n-specialist`, requires `karen`). This is one translation file.
12. Verification: Verify Japanese translations. (Agent: `karen`).

**Finalization Phase:**
13. Code Review: Review i18n setup and all translation files for completeness. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Test i18n Infrastructure: tdd-test-engineer",
    "Verify i18n Tests: karen",
    "Implement i18n Infrastructure: ui-developer",
    "Verify i18n Infrastructure: karen",
    "Create Spanish Translation: i18n-specialist",
    "Verify Spanish Translation: karen",
    "Create French Translation: i18n-specialist",
    "Verify French Translation: karen",
    "Create German Translation: i18n-specialist",
    "Verify German Translation: karen",
    "Create Japanese Translation: i18n-specialist",
    "Verify Japanese Translation: karen",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One infrastructure setup, four separate translation files. Each is atomic. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `requires-karen` agents have `karen` verification. PASS.
- CHECK 3: PARALLELIZATION - Phase 1 (1-4) is sequential as it's prerequisite infrastructure. Phase 2 (5-12) has four parallel tracks for translations that can run simultaneously. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - `code-reviewer` included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Infrastructure → ui-developer, Translations → i18n-specialist, Tests → tdd-test-engineer. PASS.
- CHECK 6: SYNCHRONIZATION - 13 todos match 13-step plan in correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Multi-Language Support

**Implementation Phase:**

*Phase 1 (Sequential - Infrastructure Setup):*
1. **Test i18n Infrastructure** - **Agent: tdd-test-engineer** - Test language detection and switching.
2. **Verify i18n Tests** - **Agent: karen** - Verify the tests.
3. **Implement i18n Infrastructure** - **Agent: ui-developer** - Set up i18next and language switcher.
4. **Verify i18n Infrastructure** - **Agent: karen** - Verify the setup.

*Phase 2 (Parallel - Translations):*
5. **Create Spanish Translation** - **Agent: i18n-specialist** - Translate all strings to Spanish.
6. **Verify Spanish Translation** - **Agent: karen** - Verify translations.
7. **Create French Translation** - **Agent: i18n-specialist** - Translate all strings to French.
8. **Verify French Translation** - **Agent: karen** - Verify translations.
9. **Create German Translation** - **Agent: i18n-specialist** - Translate all strings to German.
10. **Verify German Translation** - **Agent: karen** - Verify translations.
11. **Create Japanese Translation** - **Agent: i18n-specialist** - Translate all strings to Japanese.
12. **Verify Japanese Translation** - **Agent: karen** - Verify translations.

**Finalization Phase:**
13. **Final Code Review** - **Agent: code-reviewer** - Review all i18n implementation.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "internationalization",
            "i18n",
            "translations",
            "parallel",
            "4-tracks",
            "multi-language",
            "mixed-approach",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Implement OAuth 2.0 authentication with JWT tokens and refresh token rotation."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning OAuth authentication security JWT</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases. OAuth implementation requires both backend and UI work that can be parallelized, plus security audit is mandatory.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** OAuth implementation with parallel UI and backend development.

*Track A (Authentication Backend):*
1. TDD for OAuth Flow: Write tests for token generation, validation, and refresh token rotation. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement OAuth Backend: Create token endpoints, JWT signing/verification, and refresh logic. (Agent: `firebase-backend-architect`, requires `karen`). This is one authentication service.
4. Verification: Verify the OAuth implementation. (Agent: `karen`).

*Track B (Authentication UI):*
5. TDD for Auth UI: Write tests for login form, token storage, and automatic refresh. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
6. Verification: Verify the tests. (Agent: `karen`).
7. Implement Auth UI: Create login/logout components and token management hooks. (Agent: `ui-developer`, requires `karen`). This is one UI module.
8. Verification: Verify the UI implementation. (Agent: `karen`).

**Finalization Phase (Critical for Auth):**
9. Security Audit: Audit token storage, CSRF protection, secure flags, and compliance with OAuth 2.0 spec. (Agent: `security-auditor`).
10. Code Review: Review all authentication code for best practices. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Test OAuth Backend: tdd-test-engineer",
    "Verify OAuth Tests: karen",
    "Implement OAuth Backend: firebase-backend-architect",
    "Verify OAuth Backend: karen",
    "Test Auth UI: tdd-test-engineer",
    "Verify Auth UI Tests: karen",
    "Implement Auth UI: ui-developer",
    "Verify Auth UI: karen",
    "Security Audit: security-auditor",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - One authentication service, one UI module, each with test suites. Passes litmus test. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `requires-karen` agents have karen verification. PASS.
- CHECK 3: PARALLELIZATION - Backend (1-4) and UI (5-8) tracks can run in parallel. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Both `security-auditor` (mandatory for auth) and `code-reviewer` included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Backend → firebase-backend-architect, UI → ui-developer, Tests → tdd-test-engineer, Security → security-auditor. PASS.
- CHECK 6: SYNCHRONIZATION - 10 todos match 10-step plan in correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for OAuth 2.0 Authentication

**Implementation Phase (Parallel Tracks):**

*Track A (Authentication Backend):*
1. **Test OAuth Backend** - **Agent: tdd-test-engineer** - Test token generation and validation.
2. **Verify OAuth Tests** - **Agent: karen** - Verify the tests.
3. **Implement OAuth Backend** - **Agent: firebase-backend-architect** - Create OAuth service.
4. **Verify OAuth Backend** - **Agent: karen** - Verify the implementation.

*Track B (Authentication UI):*
5. **Test Auth UI** - **Agent: tdd-test-engineer** - Test login components.
6. **Verify Auth UI Tests** - **Agent: karen** - Verify the tests.
7. **Implement Auth UI** - **Agent: ui-developer** - Create login/logout UI.
8. **Verify Auth UI** - **Agent: karen** - Verify the UI.

**Finalization Phase:**
9. **Security Audit** - **Agent: security-auditor** - Audit token security and OAuth compliance.
10. **Final Code Review** - **Agent: code-reviewer** - Review all code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "oauth",
            "authentication",
            "security",
            "jwt",
            "parallel",
            "2-tracks",
            "security-auditor",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Create a comprehensive admin dashboard with user management, analytics charts, export functionality, and audit logging."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning admin dashboard analytics multi-feature</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases. Admin dashboard with multiple independent features - perfect for parallel development across multiple tracks.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** Admin dashboard with 4 independent feature tracks.

*Track A (User Management):*
1. TDD for User CRUD: Write tests for user list, create, edit, delete, and role management. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Implement User Management UI: Create user table, forms, and role assignment interface. (Agent: `ui-developer`, requires `karen`). This is one UI module.
4. Verification: Verify user management UI. (Agent: `karen`).
5. Implement User Management API: Create backend endpoints for user operations. (Agent: `firebase-backend-architect`, requires `karen`). This is one API module.
6. Verification: Verify user management API. (Agent: `karen`).

*Track B (Analytics Charts):*
7. TDD for Analytics: Write tests for data aggregation and chart data preparation. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
8. Verification: Verify the tests. (Agent: `karen`).
9. Implement Analytics UI: Create dashboard charts using Recharts (revenue, users, activity). (Agent: `ui-developer`, requires `karen`). This is one UI module.
10. Verification: Verify analytics UI. (Agent: `karen`).
11. Implement Analytics API: Create endpoints for time-series data aggregation. (Agent: `firebase-backend-architect`, requires `karen`). This is one API module.
12. Verification: Verify analytics API. (Agent: `karen`).

*Track C (Export Functionality):*
13. TDD for Exports: Write tests for CSV and PDF generation with proper formatting. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
14. Verification: Verify the tests. (Agent: `karen`).
15. Implement Export Service: Create backend service for report generation and downloads. (Agent: `firebase-backend-architect`, requires `karen`). This is one service.
16. Verification: Verify export service. (Agent: `karen`).

*Track D (Audit Logging):*
17. TDD for Audit Log: Write tests for event capture, storage, and querying. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
18. Verification: Verify the tests. (Agent: `karen`).
19. Implement Audit System: Create audit middleware and log viewer UI. (Agent: `firebase-backend-architect`, requires `karen`). This is one system module.
20. Verification: Verify audit system. (Agent: `karen`).

**Finalization Phase:**
21. Security Audit: Review access controls, data exposure, and audit completeness. (Agent: `security-auditor`).
22. Code Review: Review all dashboard code. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Test User CRUD: tdd-test-engineer",
    "Verify User Tests: karen",
    "Implement User Management UI: ui-developer",
    "Verify User UI: karen",
    "Implement User Management API: firebase-backend-architect",
    "Verify User API: karen",
    "Test Analytics: tdd-test-engineer",
    "Verify Analytics Tests: karen",
    "Implement Analytics UI: ui-developer",
    "Verify Analytics UI: karen",
    "Implement Analytics API: firebase-backend-architect",
    "Verify Analytics API: karen",
    "Test Exports: tdd-test-engineer",
    "Verify Export Tests: karen",
    "Implement Export Service: firebase-backend-architect",
    "Verify Export Service: karen",
    "Test Audit Log: tdd-test-engineer",
    "Verify Audit Tests: karen",
    "Implement Audit System: firebase-backend-architect",
    "Verify Audit System: karen",
    "Security Audit: security-auditor",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - Four independent features (user management, analytics, exports, audit), each with UI and API components. Each is atomic. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `requires-karen` agents have karen verification. PASS.
- CHECK 3: PARALLELIZATION - Four independent tracks (A: 1-6, B: 7-12, C: 13-16, D: 17-20) can run in parallel. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Both `security-auditor` (required for admin access) and `code-reviewer` included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - UI → ui-developer, Backend → firebase-backend-architect, Tests → tdd-test-engineer, Security → security-auditor. PASS.
- CHECK 6: SYNCHRONIZATION - 22 todos match 22-step plan in correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Admin Dashboard

**Implementation Phase (4 Parallel Tracks):**

*Track A (User Management):*
1. **Test User CRUD** - **Agent: tdd-test-engineer** - Test user operations.
2. **Verify User Tests** - **Agent: karen** - Verify the tests.
3. **Implement User Management UI** - **Agent: ui-developer** - Create user interface.
4. **Verify User UI** - **Agent: karen** - Verify the UI.
5. **Implement User Management API** - **Agent: firebase-backend-architect** - Create user API.
6. **Verify User API** - **Agent: karen** - Verify the API.

*Track B (Analytics Charts):*
7. **Test Analytics** - **Agent: tdd-test-engineer** - Test data aggregation.
8. **Verify Analytics Tests** - **Agent: karen** - Verify the tests.
9. **Implement Analytics UI** - **Agent: ui-developer** - Create charts.
10. **Verify Analytics UI** - **Agent: karen** - Verify the charts.
11. **Implement Analytics API** - **Agent: firebase-backend-architect** - Create analytics API.
12. **Verify Analytics API** - **Agent: karen** - Verify the API.

*Track C (Export Functionality):*
13. **Test Exports** - **Agent: tdd-test-engineer** - Test export generation.
14. **Verify Export Tests** - **Agent: karen** - Verify the tests.
15. **Implement Export Service** - **Agent: firebase-backend-architect** - Create export service.
16. **Verify Export Service** - **Agent: karen** - Verify the service.

*Track D (Audit Logging):*
17. **Test Audit Log** - **Agent: tdd-test-engineer** - Test audit capture.
18. **Verify Audit Tests** - **Agent: karen** - Verify the tests.
19. **Implement Audit System** - **Agent: firebase-backend-architect** - Create audit system.
20. **Verify Audit System** - **Agent: karen** - Verify the system.

**Finalization Phase:**
21. **Security Audit** - **Agent: security-auditor** - Review access controls.
22. **Final Code Review** - **Agent: code-reviewer** - Review all code.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "admin",
            "dashboard",
            "analytics",
            "complex",
            "parallel",
            "4-tracks",
            "multi-feature",
            "security-auditor",
            "cbr-retrieval",
        ],
    },
    {
        "problem": """
User: "Remediate the security findings from our latest audit: SQL injection vulnerability in search, missing rate limiting, and exposed API keys in logs."
""",
        "solution": """
<thinking>
As per my Orchestration Ritual, I must first search for planning examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration planning security remediation vulnerability fixes</query>
        <category>orchestration</category>
        <subcategory>planning</subcategory>
    </tool>
</tool_code>
<thinking>
Reviewing the planning cases. Multiple security issues can be fixed in parallel by security specialist, then audited together.
</thinking>
<tool_code>
    <tool name="mcp__sequentialthinking__sequentialthinking">
        <prompt>
**Implementation Phase (Parallel Tracks):** Three independent security fixes that can run simultaneously.

*Track A (SQL Injection Fix):*
1. TDD for SQL Fix: Write tests for parameterized queries and input sanitization. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
2. Verification: Verify the tests. (Agent: `karen`).
3. Fix SQL Injection: Replace string concatenation with parameterized queries. (Agent: `31337`, requires `karen`). This is one security fix.
4. Verification: Verify the SQL fix. (Agent: `karen`).

*Track B (Rate Limiting):*
5. TDD for Rate Limiting: Write tests for rate limit enforcement and throttling. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
6. Verification: Verify the tests. (Agent: `karen`).
7. Implement Rate Limiting: Add middleware for request rate limiting. (Agent: `31337`, requires `karen`). This is one middleware implementation.
8. Verification: Verify rate limiting works. (Agent: `karen`).

*Track C (API Key Protection):*
9. TDD for Log Sanitization: Write tests for log output to ensure no secrets are exposed. (Agent: `tdd-test-engineer`, requires `karen`). This is one test suite.
10. Verification: Verify the tests. (Agent: `karen`).
11. Sanitize Logs: Implement log sanitization and move keys to secure storage. (Agent: `31337`, requires `karen`). This is one security fix.
12. Verification: Verify log sanitization. (Agent: `karen`).

**Finalization Phase:**
13. Security Audit: Re-audit all three fixes to confirm vulnerabilities are resolved. (Agent: `security-auditor`).
14. Code Review: Review all security changes. (Agent: `code-reviewer`).
        </prompt>
    </tool>
</tool_code>

<TodoWrite>
[
    "Test SQL Fix: tdd-test-engineer",
    "Verify SQL Tests: karen",
    "Fix SQL Injection: 31337",
    "Verify SQL Fix: karen",
    "Test Rate Limiting: tdd-test-engineer",
    "Verify Rate Limit Tests: karen",
    "Implement Rate Limiting: 31337",
    "Verify Rate Limiting: karen",
    "Test Log Sanitization: tdd-test-engineer",
    "Verify Log Tests: karen",
    "Sanitize Logs: 31337",
    "Verify Log Sanitization: karen",
    "Security Audit: security-auditor",
    "Final Code Review: code-reviewer"
]
</TodoWrite>

<thinking>
Internal Checkpoint:
- CHECK 1: GRANULARITY - Three separate fixes (SQL, rate limiting, log sanitization), each atomic. PASS.
- CHECK 2: VERIFICATION COMPLIANCE - All `requires-karen` agents (tdd-test-engineer, 31337) have karen verification. PASS.
- CHECK 3: PARALLELIZATION - Three independent tracks (A: 1-4, B: 5-8, C: 9-12) can run in parallel. PASS.
- CHECK 4: FINALIZATION COMPLIANCE - Both `security-auditor` (mandatory for security work) and `code-reviewer` included. PASS.
- CHECK 5: AGENT SELECTION CORRECTNESS - Security fixes → 31337, Tests → tdd-test-engineer, Audit → security-auditor. PASS.
- CHECK 6: SYNCHRONIZATION - 14 todos match 14-step plan in correct '[Task]: [Agent]' format. PASS.

All checks passed. I am authorized to proceed.
</thinking>

## Implementation Plan for Security Remediation

**Implementation Phase (3 Parallel Tracks):**

*Track A (SQL Injection Fix):*
1. **Test SQL Fix** - **Agent: tdd-test-engineer** - Test parameterized queries.
2. **Verify SQL Tests** - **Agent: karen** - Verify the tests.
3. **Fix SQL Injection** - **Agent: 31337** - Implement parameterized queries.
4. **Verify SQL Fix** - **Agent: karen** - Verify the fix.

*Track B (Rate Limiting):*
5. **Test Rate Limiting** - **Agent: tdd-test-engineer** - Test rate limit enforcement.
6. **Verify Rate Limit Tests** - **Agent: karen** - Verify the tests.
7. **Implement Rate Limiting** - **Agent: 31337** - Add rate limiting middleware.
8. **Verify Rate Limiting** - **Agent: karen** - Verify the implementation.

*Track C (API Key Protection):*
9. **Test Log Sanitization** - **Agent: tdd-test-engineer** - Test log output safety.
10. **Verify Log Tests** - **Agent: karen** - Verify the tests.
11. **Sanitize Logs** - **Agent: 31337** - Implement log sanitization.
12. **Verify Log Sanitization** - **Agent: karen** - Verify the sanitization.

**Finalization Phase:**
13. **Security Audit** - **Agent: security-auditor** - Re-audit all fixes.
14. **Final Code Review** - **Agent: code-reviewer** - Review all changes.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": [
            "orchestration",
            "planning",
            "security",
            "remediation",
            "vulnerability",
            "parallel",
            "3-tracks",
            "security-auditor",
            "31337",
            "cbr-retrieval",
        ],
    },
]