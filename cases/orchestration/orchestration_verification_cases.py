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
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before proceeding. If karen returns "VERIFIED COMPLETE", I will mark the todo as complete and proceed to the next step. If karen returns "INCOMPLETE", I will execute the Remediation Protocol.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'ui-developer', 'requires-karen', 'component']
    },
    {
        "problem": """
After firebase-backend-architect completes the handleGoogleAuthToken function, show how to delegate to karen for backend verification.
""",
        "solution": """
The firebase-backend-architect has reported that the handleGoogleAuthToken Cloud Function is complete.

firebase-backend-architect is a requires-karen agent. I MUST delegate to karen for verification.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify handleGoogleAuthToken function</description>
        <prompt>
The firebase-backend-architect has completed the handleGoogleAuthToken Cloud Function.

Please verify this work meets all requirements:

## File to verify
functions/src/auth/handleGoogleAuthToken.ts

## Verification criteria

1. **Token Validation**: Function properly verifies Google OAuth tokens
2. **User Management**: Function correctly creates/updates user records in Firestore
3. **Session Handling**: Function creates and returns session tokens
4. **Error Handling**: Function handles invalid tokens, network failures, and database errors
5. **Security**: Proper input validation and no security vulnerabilities
6. **Type Safety**: All TypeScript types properly defined
7. **Cloud Functions Patterns**: Follows Firebase Cloud Functions v2 best practices
8. **Response Format**: Returns proper HTTP status codes and response bodies

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Briefly confirm what was verified

IF INCOMPLETE:
- State "INCOMPLETE"
- List specific issues that need to be fixed
- Be detailed enough that the firebase-backend-architect can address the issues
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before proceeding to the next step in my plan.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'firebase-backend-architect', 'requires-karen', 'backend', 'cloud-functions']
    },
    {
        "problem": """
After tdd-test-engineer completes writing tests, show how to delegate to karen to verify the tests are correct before implementation.
""",
        "solution": """
The tdd-test-engineer has completed writing tests for the Redis caching layer.

tdd-test-engineer is a requires-karen agent. I MUST delegate to karen to verify the tests before proceeding to implementation.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify Redis caching tests</description>
        <prompt>
The tdd-test-engineer has completed writing tests for the Redis caching layer in the get_product_list function.

Please verify these tests before we proceed to implementation:

## Files to verify
tests/unit/test_product_caching.rs

## Verification criteria

1. **Coverage**: Tests cover all scenarios:
   - Cache hit (data exists in Redis)
   - Cache miss (data not in Redis, fetch from DB)
   - Cache expiration
   - Cache refresh
   - Redis connection failure

2. **Test Quality**: Tests are:
   - Well-structured and readable
   - Properly isolated (mocks used correctly)
   - Following TDD principles (should fail before implementation)

3. **Assertions**: Tests have:
   - Clear, specific assertions
   - Proper error message expectations
   - Appropriate timeout handling

4. **Mock Configuration**: Redis client is:
   - Properly mocked
   - Configured with appropriate behavior for each scenario
   - Not hitting real Redis instance

5. **Project Patterns**: Tests follow:
   - Project testing conventions
   - Proper use of testing framework
   - Consistent naming patterns

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Briefly confirm test coverage and quality

IF INCOMPLETE:
- State "INCOMPLETE"
- List specific issues or missing test cases
- Identify gaps in coverage or quality concerns
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response. If "VERIFIED COMPLETE", I will proceed to delegate to rust-developer for implementation. If "INCOMPLETE", I will execute the Remediation Protocol to fix the test issues before proceeding.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'tdd-test-engineer', 'requires-karen', 'tests', 'tdd']
    },
    {
        "problem": """
After 31337 fixes security vulnerabilities, show how to delegate to karen to verify the security fixes before re-auditing.
""",
        "solution": """
The 31337 agent has completed fixing the JWT expiration validation vulnerability.

31337 is a requires-karen agent. I MUST delegate to karen to verify the security fix before proceeding to security-auditor re-audit.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify JWT expiration fix</description>
        <prompt>
The 31337 agent has completed implementing JWT expiration validation to fix the CRITICAL security vulnerability.

Please verify this security fix meets all requirements:

## Files to verify
- functions/src/auth/jwtValidation.ts
- tests/unit/test_jwt_validation.rs

## Verification criteria

1. **Expiration Validation**: Code properly:
   - Checks JWT expiration timestamp
   - Rejects expired tokens with 401 Unauthorized
   - Includes error message: "Token expired"
   - Validates before any business logic execution

2. **Test Coverage**: Tests cover:
   - Valid token scenarios
   - Expired token scenarios (various expiration dates)
   - Edge cases (just expired, far expired)
   - Error response format

3. **Security**: Implementation:
   - Follows OWASP JWT best practices
   - Prevents replay attacks with old tokens
   - Has no timing vulnerabilities
   - Properly handles malformed tokens

4. **Existing Functionality**: Changes:
   - Don't break existing authentication flow
   - Maintain all valid token acceptance
   - Preserve proper error handling for other failure modes

5. **Code Quality**:
   - Clear, maintainable code
   - Proper TypeScript types
   - No code smells or anti-patterns

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Confirm the vulnerability is properly fixed

IF INCOMPLETE:
- State "INCOMPLETE"
- List specific security concerns or implementation issues
- Identify any gaps in the fix
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response. If "VERIFIED COMPLETE", I will proceed to delegate to security-auditor for re-audit. If "INCOMPLETE", I will execute the Remediation Protocol to fix the issues identified by karen.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', '31337', 'requires-karen', 'security', 'jwt']
    },
    {
        "problem": """
After aws-devops-engineer creates a Kubernetes CronJob manifest, show how to delegate to karen for infrastructure verification.
""",
        "solution": """
The aws-devops-engineer has completed creating the Kubernetes CronJob manifest for session cleanup.

aws-devops-engineer is a requires-karen agent. I MUST delegate to karen for verification.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify Kubernetes CronJob manifest</description>
        <prompt>
The aws-devops-engineer has completed the Kubernetes CronJob manifest for running session cleanup nightly.

Please verify this infrastructure configuration:

## File to verify
k8s/cronjobs/session-cleanup.yaml

## Verification criteria

1. **Schedule Configuration**:
   - Cron expression is correct: 0 2 * * * (2 AM UTC daily)
   - Timezone handling is appropriate
   - No conflicting schedules

2. **Job Configuration**:
   - Calls the correct cleanup function/script
   - Resource limits are reasonable (CPU, memory)
   - Restart policy is appropriate (Never or OnFailure)
   - Successful jobs history limit set
   - Failed jobs history limit set

3. **RBAC and Permissions**:
   - Job has necessary service account
   - Permissions are minimal and appropriate
   - No excessive privileges

4. **Labels and Annotations**:
   - Proper labels for monitoring and organization
   - Annotations follow project conventions
   - Enables proper observability

5. **Best Practices**:
   - Follows Kubernetes manifest conventions
   - Includes helpful comments
   - Configuration is maintainable
   - No obvious security issues

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Confirm the CronJob is properly configured

IF INCOMPLETE:
- State "INCOMPLETE"
- List specific configuration issues
- Identify missing elements or misconfigurations
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before marking this task complete.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'aws-devops-engineer', 'requires-karen', 'kubernetes', 'infrastructure']
    },
    {
        "problem": """
After documentation-specialist creates component documentation, show how to delegate to karen to verify documentation completeness.
""",
        "solution": """
The documentation-specialist has completed documenting the GoogleSignInButton component.

documentation-specialist is a requires-karen agent. I MUST delegate to karen for verification.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify component documentation</description>
        <prompt>
The documentation-specialist has completed documentation for the GoogleSignInButton reusable component.

Please verify this documentation is complete and accurate:

## Files to verify
- docs/components/GoogleSignInButton.md
- Component library entry (if applicable)

## Verification criteria

1. **Purpose and Use Cases**:
   - Clear explanation of what the component does
   - When to use it / use cases listed
   - Links to related components

2. **Props Documentation**:
   - All props listed with types
   - Clear descriptions for each prop
   - Default values specified
   - Required vs optional clearly marked

3. **Usage Examples**:
   - Basic usage example provided
   - Common scenarios demonstrated
   - Integration with backend function shown
   - Code examples are syntactically correct

4. **Styling and Customization**:
   - Available styling options documented
   - Theme integration explained
   - Customization examples provided

5. **Troubleshooting**:
   - Common issues and solutions listed
   - Error scenarios explained
   - Known limitations documented

6. **Standards Compliance**:
   - Follows project documentation conventions
   - Proper formatting and structure
   - Grammar and spelling correct
   - All links working

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Confirm documentation is comprehensive and accurate

IF INCOMPLETE:
- State "INCOMPLETE"
- List missing sections or incomplete information
- Identify documentation quality issues
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before marking documentation complete.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'documentation-specialist', 'requires-karen', 'docs']
    },
    {
        "problem": """
After i18n-specialist adds internationalization, show how to delegate to karen to verify translations and i18n implementation.
""",
        "solution": """
The i18n-specialist has completed adding internationalization support to the UserProfile component.

i18n-specialist is a requires-karen agent. I MUST delegate to karen for verification.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify internationalization implementation</description>
        <prompt>
The i18n-specialist has completed adding internationalization support to the UserProfile component for all languages.

Please verify this i18n implementation:

## Files to verify
- src/components/UserProfile.tsx (refactored component)
- public/locales/en/common.json
- public/locales/es/common.json
- public/locales/fr/common.json
- public/locales/de/common.json
- public/locales/ja/common.json

## Verification criteria

1. **Translation Files**:
   - All required languages have translation files
   - Translation keys follow project conventions
   - File structure is consistent across languages
   - JSON is valid and properly formatted

2. **Component Implementation**:
   - No hardcoded strings remain in component
   - All text uses i18n library (next-i18next)
   - Translation keys are correctly referenced
   - Component renders without errors

3. **Text Coverage**:
   - All button labels translated
   - All form labels and placeholders translated
   - All error messages translated
   - All success messages translated
   - Tooltips and help text translated

4. **Functionality**:
   - Component renders correctly in all languages
   - Language switching works properly
   - Pluralization handled correctly (if applicable)
   - Date/number formatting appropriate (if applicable)

5. **Quality**:
   - Translations make sense in context
   - No missing translation keys
   - No untranslated fallback text displayed
   - Follows project i18n patterns

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Confirm all text is internationalized properly

IF INCOMPLETE:
- State "INCOMPLETE"
- List missing translations or hardcoded strings
- Identify i18n implementation issues
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before marking i18n work complete.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'i18n-specialist', 'requires-karen', 'i18n', 'translations']
    },
    {
        "problem": """
After data-scientist completes a recommendation engine, show how to delegate to karen to verify model performance and API functionality.
""",
        "solution": """
The data-scientist has completed building the product recommendation engine.

data-scientist is a requires-karen agent. I MUST delegate to karen for verification.

<tool_code>
    <tool name="Task">
        <subagent_type>karen</subagent_type>
        <description>Verify recommendation engine</description>
        <prompt>
The data-scientist has completed implementing the machine learning-based recommendation engine.

Please verify this ML implementation meets requirements:

## Files to verify
- models/recommendation_engine.py
- api/endpoints/recommendations.py
- tests/test_recommendation_engine.py
- docs/models/recommendation_engine.md

## Verification criteria

1. **Model Performance**:
   - Offline evaluation metrics meet thresholds:
     * Precision@10 >= target
     * Recall@10 >= target
     * NDCG >= target
   - A/B testing framework implemented
   - Model performance is documented

2. **API Endpoint**:
   - Endpoint returns recommendations correctly
   - Response time < 200ms (requirement)
   - Proper error handling for edge cases
   - API follows project conventions

3. **Edge Case Handling**:
   - New users (cold start) handled appropriately
   - Users with no history handled
   - Empty product catalog handled
   - Invalid user IDs handled

4. **Data Pipeline**:
   - Preprocessing implemented correctly
   - Feature engineering documented
   - Training process reproducible
   - Model can be retrained

5. **Code Quality**:
   - Clean, maintainable code
   - Proper documentation
   - Tests cover critical paths
   - No obvious performance bottlenecks

## Response format

If VERIFIED COMPLETE:
- State "VERIFIED COMPLETE"
- Confirm model performance and API functionality

IF INCOMPLETE:
- State "INCOMPLETE"
- List performance issues or missing functionality
- Identify edge cases not handled
        </prompt>
    </tool>
</tool_code>

I will wait for karen's response before marking ML work complete.
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'data-scientist', 'requires-karen', 'machine-learning', 'api']
    }
]
