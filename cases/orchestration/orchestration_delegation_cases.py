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
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'ui-developer', 'task-tool', 'proper-format', 'google-auth']
    },
    {
        "problem": """
The ui-developer has completed the GoogleSignInButton component. Show how to properly delegate the verification to karen.
""",
        "solution": """
The ui-developer has reported completion. According to the Execution Ritual, I MUST now delegate to karen for verification before marking the task complete or proceeding to the next step.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify GoogleSignInButton component</description>
        <prompt>
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

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Briefly confirm what was verified

If INCOMPLETE:
- State "INCOMPLETE"
- List specific issues that need to be fixed
- Be detailed enough that the ui-developer can address the issues
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before proceeding to the next step in the plan.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'karen', 'verification', 'blocking', 'requires-karen']
    },
    {
        "problem": """
Karen has responded with "INCOMPLETE: The button lacks a proper loading state." Show how to handle this feedback using the Remediation Protocol.
""",
        "solution": """
Karen has returned "INCOMPLETE" which is a MANDATORY REMEDIATION TRIGGER. I MUST now execute the Remediation Protocol.

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

## Step 4: Delegate the Remedial Task

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

I will wait for the ui-developer to complete the fix, then delegate back to karen for re-verification.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'remediation', 'karen-feedback', 'incomplete', 'fix-loop']
    },
    {
        "problem": """
Show how to delegate to firebase-backend-architect for backend work after the UI work is verified complete.
""",
        "solution": """
The UI work has been completed and verified. According to my plan, the next step is to create the handleGoogleAuthToken Cloud Function.

<tool_code>
    <tool name="Task">
        <subagent_type>firebase-backend-architect</subagent_type>
        <description>Create handleGoogleAuthToken Cloud Function</description>
        <prompt>
<delegate_task>
    <agent_name>firebase-backend-architect</agent_name>
    <task_objective>Create the handleGoogleAuthToken Cloud Function that processes Google OAuth tokens and creates/updates user sessions</task_objective>
    <requirements>
        - Cloud Function must accept a Google OAuth token in the request body
        - Function must verify the token with Google's OAuth API
        - Function must create or update the user record in Firestore
        - Function must create a session token and return it to the client
        - Function must handle invalid tokens gracefully with proper error responses
        - Function must follow Firebase Cloud Functions v2 patterns
        - Function must implement proper security checks and validation
        - Function must be properly typed with TypeScript
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After the firebase-backend-architect completes this function, I will delegate to karen for verification.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'firebase-backend-architect', 'backend', 'cloud-functions', 'requires-karen']
    },
    {
        "problem": """
Show how to delegate to code-reviewer for final review after all implementation and verification is complete.
""",
        "solution": """
All implementation work has been completed and verified by karen:
- GoogleSignInButton component: VERIFIED COMPLETE
- handleGoogleAuthToken function: VERIFIED COMPLETE

According to the Orchestration Ritual Finalization Phase, I MUST now delegate to code-reviewer for final review.

<tool_code>
    <tool name="Task">
        <subagent_type>code-reviewer</subagent_type>
        <description>Review Google Sign-In implementation</description>
        <prompt>
I have completed implementing Google Sign-In functionality for the application. All components have been built and verified by karen.

Please perform a comprehensive code review of the following:

## Files to review

### Frontend
- src/components/auth/GoogleSignInButton.tsx

### Backend
- functions/src/auth/handleGoogleAuthToken.ts

## Review criteria

1. **Code Quality**: Clean, maintainable, follows project conventions
2. **Security**: Proper token validation, no security vulnerabilities
3. **Error Handling**: Comprehensive error handling for all failure cases
4. **Type Safety**: All TypeScript types properly defined
5. **Testing**: Adequate test coverage (if applicable)
6. **Performance**: No obvious performance issues
7. **Integration**: Components integrate properly with existing codebase
8. **Documentation**: Code is properly documented

## Response format

If APPROVED:
- State "APPROVED"
- Provide brief summary of what was reviewed

If FAILED:
- State "FAILED"
- List specific issues that need to be addressed
- Categorize issues by severity (critical, major, minor)
        </prompt>
    </tool>
</tool_code>

Code-reviewer is a BLOCKING AUTHORITY. I CANNOT mark the overall task complete until I receive "APPROVED" from code-reviewer.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'code-reviewer', 'finalization', 'blocking-authority', 'final-review']
    },
    {
        "problem": """
Show how to delegate to security-auditor when the task involves authentication or sensitive data.
""",
        "solution": """
This task involves authentication and user data, which triggers the security-auditor requirement according to my agent directory.

After code-reviewer has approved the implementation, I MUST delegate to security-auditor because the task involves "auth, crypto, sensitive data."

<tool_code>
    <tool name="Task">
        <subagent_type>security-auditor</subagent_type>
        <description>Security audit of Google Sign-In implementation</description>
        <prompt>
I have implemented Google Sign-In functionality that handles OAuth tokens and user authentication data.

Please perform a comprehensive security audit of this implementation:

## Files to audit

### Frontend
- src/components/auth/GoogleSignInButton.tsx

### Backend
- functions/src/auth/handleGoogleAuthToken.ts

## Security audit criteria

1. **Authentication Flow**: OAuth flow is implemented correctly with no security gaps
2. **Token Handling**: Tokens are validated, stored, and transmitted securely
3. **Input Validation**: All user inputs are properly validated and sanitized
4. **Authorization**: Proper access controls are in place
5. **Data Protection**: Sensitive data (tokens, user info) is protected at rest and in transit
6. **OWASP Top 10**: No vulnerabilities from OWASP Top 10 (injection, broken auth, XSS, etc.)
7. **Session Management**: Sessions are managed securely
8. **Error Handling**: Errors don't leak sensitive information

## Response format

If APPROVED:
- State "APPROVED"
- Provide security assessment summary

If FAILED:
- State "FAILED"
- List all security vulnerabilities found
- Categorize by severity: CRITICAL, HIGH, MEDIUM, LOW
- Provide remediation guidance for each issue
        </prompt>
    </tool>
</tool_code>

Security-auditor is a BLOCKING AUTHORITY. I CANNOT mark the task complete until I receive "APPROVED" from security-auditor.

If security-auditor responds with "FAILED", I MUST execute the Remediation Protocol.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'security-auditor', 'finalization', 'blocking-authority', 'authentication', 'security']
    },
    {
        "problem": """
Show how to delegate to product-strategist when the user request is ambiguous or requires planning.
""",
        "solution": """
User: "I want to improve the user experience of our dashboard."

This request is ambiguous - it's unclear what specific improvements are needed. According to my agent directory, ambiguous requests trigger delegation to product-strategist.

<tool_code>
    <tool name="Task">
        <subagent_type>product-strategist</subagent_type>
        <description>Analyze dashboard UX improvement requirements</description>
        <prompt>
<delegate_task>
    <agent_name>product-strategist</agent_name>
    <task_objective>Analyze the current dashboard user experience and create a detailed specification for improvements</task_objective>
    <requirements>
        - Review the existing dashboard implementation
        - Identify specific UX pain points and improvement opportunities
        - Prioritize improvements by impact and effort
        - Create a detailed specification document with:
          * Current state analysis
          * Specific UX improvements to implement
          * User stories for each improvement
          * Success metrics
          * Implementation approach recommendations
        - Ensure improvements align with product mission and roadmap
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After product-strategist completes the analysis, I will delegate to karen to verify the specification is complete and actionable.

Once verified, I will create a new implementation plan based on the product-strategist's detailed specification.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'product-strategist', 'ambiguous-request', 'planning', 'ux', 'requires-karen']
    },
    {
        "problem": """
Show how to delegate to documentation-specialist after creating a new reusable component.
""",
        "solution": """
I have completed implementing the GoogleSignInButton component, and it has been verified by karen and approved by code-reviewer.

According to my agent directory, new reusable components trigger the documentation-specialist agent. This component will be reused across the application, so documentation is required.

<tool_code>
    <tool name="Task">
        <subagent_type>documentation-specialist</subagent_type>
        <description>Document GoogleSignInButton component</description>
        <prompt>
<delegate_task>
    <agent_name>documentation-specialist</agent_name>
    <task_objective>Create comprehensive documentation for the GoogleSignInButton reusable React component</task_objective>
    <requirements>
        - Document the component's purpose and use cases
        - List all props with types, descriptions, and examples
        - Provide usage examples for common scenarios
        - Document styling and customization options
        - Include integration examples showing how to connect with the handleGoogleAuthToken backend function
        - Add troubleshooting section for common issues
        - Follow the project's component documentation standards
        - Create or update the component in the project's component library docs
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After documentation-specialist completes the documentation, I will delegate to karen for verification to ensure documentation is complete and accurate.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'documentation-specialist', 'reusable-component', 'docs', 'requires-karen']
    },
    {
        "problem": """
Show how to delegate to tdd-test-engineer before implementation work begins.
""",
        "solution": """
User: "Add a Redis caching layer for the get_product_list function."

According to the agent directory, test implementation ALWAYS happens before implementation. I must delegate to tdd-test-engineer first.

<tool_code>
    <tool name="Task">
        <subagent_type>tdd-test-engineer</subagent_type>
        <description>Write tests for Redis caching</description>
        <prompt>
<delegate_task>
    <agent_name>tdd-test-engineer</agent_name>
    <task_objective>Write comprehensive tests for the Redis caching layer in the get_product_list function before implementation begins</task_objective>
    <requirements>
        - Write test cases for cache hit scenario (data exists in Redis)
        - Write test cases for cache miss scenario (data not in Redis, must fetch from DB)
        - Write test cases for cache expiration and refresh
        - Write test cases for error handling (Redis connection failure, etc.)
        - Mock the Redis client appropriately
        - Ensure tests follow TDD principles (they should fail until implementation is complete)
        - Use the project's testing framework and patterns
        - Achieve comprehensive coverage of the caching logic
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After tdd-test-engineer completes the tests, I will:
1. Delegate to karen to verify the tests
2. Delegate to rust-developer to implement the caching layer
3. Delegate to karen to verify the implementation passes all tests
4. Delegate to code-reviewer for final review

This follows the TDD workflow: tests first, implementation second.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'tdd-test-engineer', 'tdd', 'tests-first', 'redis', 'requires-karen']
    },
    {
        "problem": """
Show how to delegate to debug-specialist when encountering a bug with unknown cause.
""",
        "solution": """
User: "The /api/v1/analytics/report endpoint is timing out intermittently. I'm not sure why."

The cause of this issue is unknown. According to my agent directory, "unknown bug cause" triggers the debug-specialist agent.

<tool_code>
    <tool name="Task">
        <subagent_type>debug-specialist</subagent_type>
        <description>Investigate analytics endpoint timeout</description>
        <prompt>
<delegate_task>
    <agent_name>debug-specialist</agent_name>
    <task_objective>Investigate and identify the root cause of intermittent timeouts in the /api/v1/analytics/report endpoint</task_objective>
    <requirements>
        - Analyze the endpoint implementation to identify potential bottlenecks
        - Check for N+1 query issues, slow database queries, or inefficient algorithms
        - Review error logs and timing data for patterns
        - Identify whether the issue is:
          * Database performance
          * External API calls
          * Computational complexity
          * Memory issues
          * Network problems
        - Provide a detailed root cause analysis
        - Recommend specific fixes for the identified issue(s)
        - Estimate the performance improvement expected from each fix
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

Debug-specialist does NOT require karen verification because it's an investigation task, not an implementation task.

After debug-specialist completes the investigation and provides a root cause analysis, I will create a new implementation plan to fix the identified issues.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'debug-specialist', 'investigation', 'performance', 'unknown-bug', 'no-karen']
    },
    {
        "problem": """
Show how to delegate to aws-devops-engineer for infrastructure work.
""",
        "solution": """
User: "Create a Kubernetes CronJob YAML to run the session cleanup nightly at 2 AM UTC."

This is infrastructure and DevOps work. According to my agent directory, this triggers the aws-devops-engineer agent.

<tool_code>
    <tool name="Task">
        <subagent_type>aws-devops-engineer</subagent_type>
        <description>Create Kubernetes CronJob for session cleanup</description>
        <prompt>
<delegate_task>
    <agent_name>aws-devops-engineer</agent_name>
    <task_objective>Create a Kubernetes CronJob configuration that runs the session cleanup script nightly at 2 AM UTC</task_objective>
    <requirements>
        - Create a Kubernetes CronJob YAML manifest
        - Schedule: 0 2 * * * (2 AM UTC daily)
        - Job should call the existing session cleanup function
        - Configure appropriate resource limits (CPU, memory)
        - Set successful jobs history limit and failed jobs history limit
        - Configure restart policy appropriately
        - Add proper labels and annotations for monitoring
        - Ensure the job has necessary RBAC permissions
        - Follow the project's Kubernetes manifest conventions
        - Include comments explaining the configuration
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After aws-devops-engineer completes the CronJob manifest, I will delegate to karen to verify the configuration is correct and follows best practices.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'aws-devops-engineer', 'kubernetes', 'cronjob', 'infrastructure', 'requires-karen']
    },
    {
        "problem": """
Show how to delegate to 31337 when remediating security findings.
""",
        "solution": """
The security-auditor has completed the audit and responded with:

"FAILED: Found 3 security vulnerabilities:
- CRITICAL: JWT tokens not validated for expiration
- HIGH: Password reset tokens stored in plaintext
- MEDIUM: Missing rate limiting on login endpoint"

This is a "remediate security findings" scenario, which triggers the 31337 agent according to my agent directory.

<tool_code>
    <tool name="Task">
        <subagent_type>31337</subagent_type>
        <description>Remediate security vulnerabilities</description>
        <prompt>
<delegate_task>
    <agent_name>31337</agent_name>
    <task_objective>Fix all security vulnerabilities identified by the security-auditor in the authentication implementation</task_objective>
    <requirements>
        Security vulnerabilities to fix:

        1. CRITICAL: JWT tokens not validated for expiration
           - Implement proper JWT expiration validation
           - Reject expired tokens with appropriate error response

        2. HIGH: Password reset tokens stored in plaintext
           - Hash password reset tokens before storing
           - Use cryptographically secure hashing (bcrypt or similar)

        3. MEDIUM: Missing rate limiting on login endpoint
           - Implement rate limiting to prevent brute force attacks
           - Configure appropriate limits (e.g., 5 attempts per minute)
           - Return 429 Too Many Requests when limit exceeded

        Additional requirements:
        - Maintain all existing functionality
        - Ensure fixes follow security best practices
        - Add appropriate error handling
        - Update any affected tests
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After 31337 completes the security fixes, I will:
1. Delegate to karen to verify the fixes
2. Delegate to security-auditor to re-audit and confirm vulnerabilities are resolved
3. Delegate to code-reviewer for final review

31337 is a requires-karen agent, so karen verification is mandatory before proceeding.
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', '31337', 'security', 'remediation', 'vulnerabilities', 'requires-karen']
    },
    {
        "problem": """
Show how to delegate to i18n-specialist after UI components are created.
""",
        "solution": """
The ui-developer has completed the UserProfile component and karen has verified it. The component contains user-facing text that needs internationalization.

According to my agent directory, "internationalization needed" triggers the i18n-specialist agent.

<tool_code>
    <tool name="Task">
        <subagent_type>i18n-specialist</subagent_type>
        <description>Internationalize UserProfile component</description>
        <prompt>
<delegate_task>
    <agent_name>i18n-specialist</agent_name>
    <task_objective>Add internationalization support to the UserProfile component for all supported languages</task_objective>
    <requirements>
        - Identify all user-facing text in the UserProfile component
        - Create translation keys using the project's i18n key naming conventions
        - Add translation files for all supported languages (en, es, fr, de, ja)
        - Refactor the component to use the i18n library (next-i18next)
        - Ensure all text, including:
          * Button labels
          * Form field labels and placeholders
          * Error messages
          * Success messages
          * Tooltips and help text
        - Follow the project's i18n patterns and conventions
        - Maintain the component's existing functionality
        - Ensure proper handling of pluralization and formatting
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After i18n-specialist completes the internationalization, I will delegate to karen to verify:
- Translation files are properly structured
- All text has been internationalized (no hardcoded strings)
- The component renders correctly in all languages
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'i18n-specialist', 'internationalization', 'ui', 'requires-karen']
    },
    {
        "problem": """
Show how to delegate to data-scientist for machine learning or analytics work.
""",
        "solution": """
User: "Create a recommendation engine that suggests products to users based on their browsing history."

This is a machine learning task. According to my agent directory, "machine learning" triggers the data-scientist agent.

<tool_code>
    <tool name="Task">
        <subagent_type>data-scientist</subagent_type>
        <description>Build product recommendation engine</description>
        <prompt>
<delegate_task>
    <agent_name>data-scientist</agent_name>
    <task_objective>Design and implement a machine learning-based recommendation engine that suggests products to users based on their browsing history</task_objective>
    <requirements>
        - Analyze available data (user browsing history, product catalog, purchase data)
        - Design recommendation algorithm (collaborative filtering, content-based, or hybrid)
        - Implement data preprocessing and feature engineering pipeline
        - Train and evaluate the recommendation model
        - Create API endpoint to serve recommendations
        - Implement A/B testing framework to measure recommendation quality
        - Document model architecture, training process, and performance metrics
        - Ensure recommendations can be generated in real-time (<200ms)
        - Include offline evaluation metrics (precision@k, recall@k, NDCG)
        - Consider cold start problem for new users/products
    </requirements>
    <critical>You MUST NOT delegate this work to other agents. You are responsible for completing it.</critical>
</delegate_task>
        </prompt>
    </tool>
</tool_code>

After data-scientist completes the recommendation engine, I will delegate to karen to verify:
- Model performance meets requirements
- API endpoint functions correctly
- Recommendations are relevant and high-quality
- System handles edge cases (new users, empty history, etc.)
""",
        "category": 'orchestration',
        "subcategory": 'delegation',
        "tags": ['orchestration', 'delegation', 'data-scientist', 'machine-learning', 'recommendations', 'ai', 'requires-karen']
    }
]
