"""
Orchestration Planning Cases for CBR MCP Server
Examples: TDD workflow planning, multi-agent task breakdown
"""

ORCHESTRATION_PLANNING_CASES = [
    {
        "problem": "Refactor the PaymentProcessor service to use the new StripeClient instead of the legacy BraintreeClient.",
        "solution": """
<sequential-thinking>
The user wants to refactor a service. This involves changing implementation details while ensuring behavior remains the same. A Test-Driven Development (TDD) approach is safest.

1.  **Write Refactoring Tests:** Ensure existing tests cover all legacy client behavior. Write new tests for the StripeClient if needed.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Refactor:** Swap the BraintreeClient with the new StripeClient.
    -   Agent: rust-developer
    -   Verification: karen (ensure all tests pass)
3.  **Final Review:** Review the refactored code for quality and correctness.
    -   Agent: code-reviewer (blocking)

This translates to 5 delegation steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write integration tests for the PaymentProcessor service using the new StripeClient",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write refactoring tests"
    },
    {
        "content": "Delegate to karen to verify the new tests for the PaymentProcessor service",
        "status": "pending",
        "activeForm": "Delegating to karen to verify refactoring tests"
    },
    {
        "content": "Delegate to rust-developer to refactor the PaymentProcessor service to use StripeClient",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement refactor"
    },
    {
        "content": "Delegate to karen to verify the PaymentProcessor refactor passes all tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify refactor implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the refactored PaymentProcessor service code",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for PaymentProcessor Refactor

1.  **Write Tests:** Delegate to **tdd-test-engineer** to create tests ensuring the new `StripeClient` behaves as expected within the `PaymentProcessor`.
2.  **Verify Tests:** Delegate to **karen** to confirm test quality and coverage.
3.  **Implement Refactor:** Delegate to **rust-developer** to perform the refactoring.
4.  **Verify Implementation:** Delegate to **karen** to ensure all existing and new tests pass.
5.  **Code Review:** Delegate to **code-reviewer** for a final quality check.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": ["tdd", "test-driven", "workflow", "planning", "agents", "refactoring", "orchestration", "delegation", "testing", "rust", "stripe", "payment-processing"]
    },
    {
        "problem": "Add a last_login_ip field to the User model in the database.",
        "solution": """
<sequential-thinking>
This is a database migration and a code change. It requires updating the database schema, the data access layer, and the application code that uses it.

1.  **Write Migration Tests:** Test that the repository can handle the new `last_login_ip` field.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Model/Repository Change:** Add the field to the `User` struct and update the repository logic.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Write Migration Script:** Create the database migration script to add the new column.
    -   Agent: aws-devops-engineer (as they handle infrastructure/DB schema)
    -   Verification: karen (verify script syntax and safety)
4.  **Final Review:** Review all code changes.
    -   Agent: code-reviewer

This results in 7 delegation steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the UserRepository to handle the last_login_ip field",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write repository tests"
    },
    {
        "content": "Delegate to karen to verify the UserRepository tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to add the last_login_ip field to the User model and repository",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to update model"
    },
    {
        "content": "Delegate to karen to verify the User model implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to aws-devops-engineer to write a SurrealDB migration script to add the last_login_ip field",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to write migration"
    },
    {
        "content": "Delegate to karen to verify the database migration script",
        "status": "pending",
        "activeForm": "Delegating to karen to verify migration script"
    },
    {
        "content": "Delegate to code-reviewer to review all changes related to the new field",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for Adding `last_login_ip` Field

1.  **Write Repository Tests:** Delegate to **tdd-test-engineer** to test the data access layer.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Update Code:** Delegate to **rust-developer** to update the application code.
4.  **Verify Code:** Delegate to **karen** to verify the code changes.
5.  **Write Migration Script:** Delegate to **aws-devops-engineer** to create the DB migration script.
6.  **Verify Migration Script:** Delegate to **karen** to verify the script.
7.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
""",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": ["orchestration", "planning", "agents", "tasks", "tdd", "workflow", "database", "migration", "multi-agent", "coordination", "delegation", "rust", "surrealdb"]
    },
    {
        "problem": "Integrate with the WeatherAPI to fetch the current weather for a user's location.",
        "solution": """
<sequential-thinking>
This involves creating a new client to communicate with an external API.

1.  **Write WeatherAPI Client Tests:** Create tests for a new service that will call the WeatherAPI.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement WeatherAPI Client:** Build the client.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Final Review:** Review the new client code.
    -   Agent: code-reviewer

This is a 5-step delegation process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for a new WeatherAPI client service",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write client tests"
    },
    {
        "content": "Delegate to karen to verify the WeatherAPI client tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the WeatherAPI client",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement client"
    },
    {
        "content": "Delegate to karen to verify the WeatherAPI client implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new WeatherAPI client",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for WeatherAPI Integration

1.  **Write Client Tests:** Delegate to **tdd-test-engineer** to create tests for the new API client.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Client:** Delegate to **rust-developer** to build the client.
4.  **Verify Implementation:** Delegate to **karen** to verify the implementation.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "The /api/v1/analytics/report endpoint is too slow. Find the bottleneck and optimize it.",
        "solution": """
<sequential-thinking>
The user is reporting a performance issue with an unknown cause. The first step is investigation.

1.  **Debug Performance:** Use the `debug-specialist` to analyze the endpoint, find the performance bottleneck (e.g., N+1 query, slow computation), and recommend a fix.
    -   Agent: debug-specialist

The fix will require a new plan after the investigation is complete.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to debug-specialist to investigate and identify the performance bottleneck in the /api/v1/analytics/report endpoint",
        "status": "pending",
        "activeForm": "Delegating to debug-specialist to investigate performance"
    }
]
</TodoWrite>

## Plan for Performance Investigation

1.  **Investigate Bottleneck:** I will delegate to the **debug-specialist** to analyze the slow endpoint and provide a root cause analysis with a recommended solution.

Once the analysis is complete, I will formulate a new plan to implement the fix.

Do you approve this investigation plan?
"""
    },
    {
        "problem": "Add internationalization support for French to the <UserProfile> component.",
        "solution": """
<sequential-thinking>
This is an internationalization (i18n) task, which requires a specialist.

1.  **Create Translation Files:** Add the necessary French (fr) translation files for all text in the `<UserProfile>` component.
    -   Agent: i18n-specialist
    -   Verification: karen (verify files exist and have correct keys)
2.  **Implement i18n in Component:** Refactor the `<UserProfile>` component to use the i18n library to display the translated text.
    -   Agent: ui-developer
    -   Verification: karen (verify component renders correctly with French text)
3.  **Final Review:**
    -   Agent: code-reviewer

This is a 5-step delegation process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to i18n-specialist to create French translation files for the UserProfile component",
        "status": "pending",
        "activeForm": "Delegating to i18n-specialist to add translations"
    },
    {
        "content": "Delegate to karen to verify the French translation files are correctly structured",
        "status": "pending",
        "activeForm": "Delegating to karen to verify translation files"
    },
    {
        "content": "Delegate to ui-developer to refactor the UserProfile component to use the i18n library",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to implement i18n"
    },
    {
        "content": "Delegate to karen to verify the UserProfile component correctly displays French translations",
        "status": "pending",
        "activeForm": "Delegating to karen to verify i18n implementation"
    },
    {
        "content": "Delegate to code-reviewer to review all i18n changes",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for Internationalization

1.  **Create Translations:** Delegate to **i18n-specialist** to add French translation files.
2.  **Verify Translations:** Delegate to **karen** to check the new files.
3.  **Implement in Component:** Delegate to **ui-developer** to update the component to use the translations.
4.  **Verify Implementation:** Delegate to **karen** to confirm the component renders correctly.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Implement a feature flag for the new 'AI Summary' feature.",
        "solution": """
<sequential-thinking>
This involves both backend logic to check the flag and potentially frontend work to show/hide the feature. I'll focus on the backend implementation first.

1.  **TDD for Flag Logic:** Write tests for the service that will check if the 'AI Summary' feature flag is enabled.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Flag Check:** Implement the logic.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Code Review:**
    -   Agent: code-reviewer

This breaks down into 5 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the feature flag checking logic for 'AI Summary'",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write tests"
    },
    {
        "content": "Delegate to karen to verify the feature flag tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the feature flag check for 'AI Summary'",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement logic"
    },
    {
        "content": "Delegate to karen to verify the feature flag implementation passes tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the feature flag implementation",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Feature Flag Implementation

1.  **Write Tests:** Delegate to **tdd-test-engineer** to create tests for the flag logic.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Logic:** Delegate to **rust-developer** to add the feature flag check.
4.  **Verify Implementation:** Delegate to **karen** to verify the implementation.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Scaffold a new microservice for handling user notifications.",
        "solution": """
<sequential-thinking>
Scaffolding a new service from a template is a DevOps task.

1.  **Scaffold Service:** Use the company's microservice template to create the basic project structure for the `notifications-service`.
    -   Agent: aws-devops-engineer
    -   Verification: karen (verify the project builds and default tests pass)

This is a 2-step process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to aws-devops-engineer to scaffold the new notifications-service from the standard template",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to scaffold service"
    },
    {
        "content": "Delegate to karen to verify the new service builds and passes initial checks",
        "status": "pending",
        "activeForm": "Delegating to karen to verify scaffolding"
    }
]
</TodoWrite>

## Plan for New Microservice

1.  **Scaffold Service:** Delegate to **aws-devops-engineer** to create the new service from the project template.
2.  **Verify:** Delegate to **karen** to ensure the newly created service is valid and buildable.

Do you approve this plan?
"""
    },
    {
        "problem": "Update the Dockerfile and CI/CD pipeline to use the new base image rust:1.79-slim.",
        "solution": """
<sequential-thinking>
This is a pure DevOps and infrastructure change.

1.  **Update Files:** Modify the `Dockerfile` and `.github/workflows/ci.yml` to use the new base image.
    -   Agent: aws-devops-engineer
    -   Verification: karen (verify the CI pipeline completes successfully with the new image)

This is a simple 2-step delegation.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to aws-devops-engineer to update Dockerfile and CI pipeline to use rust:1.79-slim",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to update files"
    },
    {
        "content": "Delegate to karen to verify that the CI pipeline passes with the new base image",
        "status": "pending",
        "activeForm": "Delegating to karen to verify pipeline"
    }
]
</TodoWrite>

## Plan for CI/CD Update

1.  **Update Infrastructure Files:** Delegate to **aws-devops-engineer** to update the necessary configuration files.
2.  **Verify Changes:** Delegate to **karen** to trigger and verify the CI pipeline to confirm the change is working.

Do you approve this plan?
"""
    },
    {
        "problem": "Remove the deprecated LegacyReporting module and all its usages.",
        "solution": """
<sequential-thinking>
Removing code requires careful testing to ensure no regressions are introduced.

1.  **Write Tests:** Write characterization tests around the code that uses the `LegacyReporting` module to lock down its current behavior.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Remove Module:** Delete the `LegacyReporting` module and refactor the code that used it.
    -   Agent: rust-developer
    -   Verification: karen (ensure all tests still pass)
3.  **Final Review:**
    -   Agent: code-reviewer

This breaks down into 5 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write characterization tests for code using LegacyReporting",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write tests"
    },
    {
        "content": "Delegate to karen to verify the new characterization tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to remove the LegacyReporting module and refactor its usages",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to remove module"
    },
    {
        "content": "Delegate to karen to verify that all tests pass after removing the module",
        "status": "pending",
        "activeForm": "Delegating to karen to verify removal"
    },
    {
        "content": "Delegate to code-reviewer to review the removal of the LegacyReporting module",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Deprecation Removal

1.  **Write Tests:** Delegate to **tdd-test-engineer** to write tests to prevent regressions.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Remove Code:** Delegate to **rust-developer** to perform the code removal and refactoring.
4.  **Verify Removal:** Delegate to **karen** to run all tests and confirm success.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Fix the accessibility issues on the login form. It is missing labels and has poor color contrast.",
        "solution": """
<sequential-thinking>
This is a UI and accessibility (a11y) task.

1.  **Fix A11y Issues:** Update the login form component to add proper `aria-labels` and adjust the CSS to meet WCAG color contrast standards.
    -   Agent: ui-developer
    -   Verification: karen (run an automated accessibility checker like Axe and verify the specific issues are resolved)
2.  **Final Review:**
    -   Agent: code-reviewer

This is a 3-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to ui-developer to fix accessibility issues on the login form",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to fix a11y issues"
    },
    {
        "content": "Delegate to karen to verify the accessibility fixes using an automated checker",
        "status": "pending",
        "activeForm": "Delegating to karen to verify a11y fixes"
    },
    {
        "content": "Delegate to code-reviewer to review the accessibility improvements",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Accessibility Fixes

1.  **Implement Fixes:** Delegate to **ui-developer** to update the login form's code and styles.
2.  **Verify Fixes:** Delegate to **karen** to run accessibility checks and confirm the issues are resolved.
3.  **Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Add structured logging to the authentication service.",
        "solution": """
<sequential-thinking>
This involves adding logging statements at key points in the authentication flow.

1.  **TDD for Logging:** Write tests that mock the logger and assert that it's called with the correct structured data on login success and failure.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Logging:** Add the logging statements to the authentication service code.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Code Review:**
    -   Agent: code-reviewer

This is a 5-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for structured logging in the authentication service",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write logging tests"
    },
    {
        "content": "Delegate to karen to verify the logging tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement structured logging in the authentication service",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement logging"
    },
    {
        "content": "Delegate to karen to verify the logging implementation passes all tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new logging implementation",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Structured Logging

1.  **Write Tests:** Delegate to **tdd-test-engineer** to create tests that verify logging output.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Logging:** Delegate to **rust-developer** to add the logging code.
4.  **Verify Implementation:** Delegate to **karen** to confirm tests pass.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Create a nightly cron job that cleans up expired user sessions from the database.",
        "solution": """
<sequential-thinking>
This requires two distinct parts: the cleanup logic and the scheduling mechanism.

1.  **TDD for Cleanup Logic:** Write tests for the function that will delete expired sessions.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Cleanup Logic:** Write the session cleanup function.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Schedule Cron Job:** Create the infrastructure configuration (e.g., a Kubernetes CronJob YAML or an AWS Lambda scheduled event) to run the cleanup logic nightly.
    -   Agent: aws-devops-engineer
    -   Verification: karen (verify the job is scheduled in the target environment)
4.  **Code Review:** Review the cleanup logic code.
    -   Agent: code-reviewer

Total of 7 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the expired session cleanup logic",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write cleanup tests"
    },
    {
        "content": "Delegate to karen to verify the cleanup logic tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the expired session cleanup logic",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement cleanup logic"
    },
    {
        "content": "Delegate to karen to verify the cleanup logic implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to aws-devops-engineer to create and schedule the nightly cron job",
        "status": "pending",
        "activeForm": "Delegating to aws-devops-engineer to schedule job"
    },
    {
        "content": "Delegate to karen to verify the cron job is scheduled correctly",
        "status": "pending",
        "activeForm": "Delegating to karen to verify scheduling"
    },
    {
        "content": "Delegate to code-reviewer to review the session cleanup code",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Session Cleanup Cron Job

1.  **Write Logic Tests:** Delegate to **tdd-test-engineer** for the cleanup logic.
2.  **Verify Logic Tests:** Delegate to **karen**.
3.  **Implement Logic:** Delegate to **rust-developer** to write the cleanup function.
4.  **Verify Logic:** Delegate to **karen**.
5.  **Schedule Job:** Delegate to **aws-devops-engineer** to set up the cron job infrastructure.
6.  **Verify Schedule:** Delegate to **karen**.
7.  **Code Review:** Delegate to **code-reviewer**.

Do you approve this plan?
"""
    },
    {
        "problem": "Add server-side validation to the user registration endpoint for password strength.",
        "solution": """
<sequential-thinking>
This is a classic TDD case for modifying an existing endpoint.

1.  **Write Failing Tests:** Add new tests to the registration endpoint test suite that assert a 400 Bad Request is returned for weak passwords.
    -   Agent: tdd-test-engineer
    -   Verification: karen (verify the new tests fail as expected)
2.  **Implement Validation:** Add the password validation logic to the registration endpoint handler.
    -   Agent: rust-developer
    -   Verification: karen (verify all tests, including the new ones, now pass)
3.  **Security Audit:** Since this touches authentication, a security review is required.
    -   Agent: security-auditor (blocking)

This results in 5 delegation steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write failing tests for password strength validation",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write failing tests"
    },
    {
        "content": "Delegate to karen to verify the new password tests fail correctly",
        "status": "pending",
        "activeForm": "Delegating to karen to verify failing tests"
    },
    {
        "content": "Delegate to rust-developer to implement the password strength validation logic",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement validation"
    },
    {
        "content": "Delegate to karen to verify the validation implementation passes all tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to security-auditor to audit the new password validation logic",
        "status": "pending",
        "activeForm": "Delegating to security-auditor for audit"
    }
]
</TodoWrite>

## Plan for Password Validation

1.  **Write Failing Tests:** Delegate to **tdd-test-engineer** to add tests for the new validation rules.
2.  **Verify Failing Tests:** Delegate to **karen** to confirm the tests fail as expected.
3.  **Implement Validation:** Delegate to **rust-developer** to add the server-side logic.
4.  **Verify Implementation:** Delegate to **karen** to confirm all tests now pass.
5.  **Security Audit:** Delegate to **security-auditor** for a final security review.

Do you approve this plan?
"""
    },
    {
        "problem": "Implement a Redis caching layer for the get_product_list function.",
        "solution": """
<sequential-thinking>
This involves modifying an existing function to add caching logic.

1.  **TDD for Caching:** Write tests for the `get_product_list` function that cover cache hit and cache miss scenarios.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Caching:** Modify the function to include logic to check Redis for cached data before hitting the database.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Code Review:**
    -   Agent: code-reviewer

This is a 5-step process.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for Redis caching in get_product_list",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write caching tests"
    },
    {
        "content": "Delegate to karen to verify the caching tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the Redis caching layer for get_product_list",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement caching"
    },
    {
        "content": "Delegate to karen to verify the caching implementation passes all tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new caching implementation",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Caching Layer

1.  **Write Tests:** Delegate to **tdd-test-engineer** to test cache hit/miss scenarios.
2.  **Verify Tests:** Delegate to **karen** to verify the tests.
3.  **Implement Caching:** Delegate to **rust-developer** to add the Redis logic.
4.  **Verify Implementation:** Delegate to **karen** to verify the implementation.
5.  **Final Code Review:** Delegate to **code-reviewer** for a final review.

Do you approve this plan?
"""
    },
    {
        "problem": "Create a new GET endpoint /api/v1/health that returns a 200 OK.",
        "solution": """
<sequential-thinking>
This is a very simple, standard backend task. The full TDD workflow should still be followed for consistency.

1.  **Write Tests:** Create a test file for the health endpoint that asserts a 200 status code and expected JSON body.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Endpoint:** Create the route and handler for `/api/v1/health`.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Final Review:**
    -   Agent: code-reviewer

A 5-step delegation.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the /api/v1/health endpoint",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to write health tests"
    },
    {
        "content": "Delegate to karen to verify the health endpoint tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to rust-developer to implement the /api/v1/health endpoint",
        "status": "pending",
        "activeForm": "Delegating to rust-developer to implement endpoint"
    },
    {
        "content": "Delegate to karen to verify the health endpoint implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to code-reviewer to review the new health endpoint code",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for Health Endpoint

1.  **Write Tests:** Delegate to **tdd-test-engineer**.
2.  **Verify Tests:** Delegate to **karen**.
3.  **Implement Endpoint:** Delegate to **rust-developer**.
4.  **Verify Implementation:** Delegate to **karen**.
5.  **Code Review:** Delegate to **code-reviewer**.

Do you approve this plan?
"""
    },
    {
        "problem": "Migrate the state management in the Dashboard page from local state to a global Zustand store.",
        "solution": """
<sequential-thinking>
This is a frontend refactoring task. It should be broken into creating the store and then using the store.

1.  **TDD for Zustand Store:** Write tests for the new global dashboard store, covering its actions and initial state.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement Zustand Store:** Create the Zustand store file.
    -   Agent: ui-developer
    -   Verification: karen
3.  **TDD for Component Refactor:** Write tests for the Dashboard page that mock the new store and assert correct rendering.
    -   Agent: tdd-test-engineer
    -   Verification: karen
4.  **Implement Component Refactor:** Refactor the Dashboard component to use the new store instead of local state.
    -   Agent: ui-developer
    -   Verification: karen
5.  **Code Review:**
    -   Agent: code-reviewer

This is a 9-step plan.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the new Dashboard Zustand store",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to test store"
    },
    {
        "content": "Delegate to karen to verify the Zustand store tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement the Dashboard Zustand store",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to implement store"
    },
    {
        "content": "Delegate to karen to verify the Zustand store implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify store"
    },
    {
        "content": "Delegate to tdd-test-engineer to write tests for the refactored Dashboard component",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer to test component"
    },
    {
        "content": "Delegate to karen to verify the refactored component tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to refactor the Dashboard component to use the Zustand store",
        "status": "pending",
        "activeForm": "Delegating to ui-developer to refactor component"
    },
    {
        "content": "Delegate to karen to verify the refactored Dashboard component implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify component"
    },
    {
        "content": "Delegate to code-reviewer to review the state management migration",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for review"
    }
]
</TodoWrite>

## Plan for State Management Migration

1.  **Test Store:** Delegate to **tdd-test-engineer** to test the new store.
2.  **Verify Store Tests:** Delegate to **karen**.
3.  **Implement Store:** Delegate to **ui-developer** to create the store.
4.  **Verify Store:** Delegate to **karen**.
5.  **Test Component:** Delegate to **tdd-test-engineer** to test the refactored component.
6.  **Verify Component Tests:** Delegate to **karen**.
7.  **Implement Component Refactor:** Delegate to **ui-developer**.
8.  **Verify Component Refactor:** Delegate to **karen**.
9.  **Code Review:** Delegate to **code-reviewer**.

Do you approve this plan?
"""
    },
    {
        "problem": "Create a reusable React component for a data table with sorting and pagination.",
        "solution": """
<sequential-thinking>
This is a complex UI feature that should be broken down into smaller pieces. Let's start with the core table functionality.

1.  **TDD for DataTable Component:** Write tests for a basic `<DataTable>` component that renders rows and columns.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Implement DataTable Component:**
    -   Agent: ui-developer
    -   Verification: karen
3.  **TDD for Sorting Logic:** Write tests for the sorting functionality.
    -   Agent: tdd-test-engineer
    -   Verification: karen
4.  **Implement Sorting Logic:** Add sorting to the `<DataTable>`.
    -   Agent: ui-developer
    -   Verification: karen
5.  **TDD for Pagination Logic:** Write tests for the pagination controls.
    -   Agent: tdd-test-engineer
    -   Verification: karen
6.  **Implement Pagination Logic:** Add pagination to the `<DataTable>`.
    -   Agent: ui-developer
    -   Verification: karen
7.  **Documentation:** Document the new component's props and usage.
    -   Agent: documentation-specialist
    -   Verification: karen
8.  **Code Review:**
    -   Agent: code-reviewer

This plan has 15 steps.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to tdd-test-engineer to write tests for the base DataTable component",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer for base table tests"
    },
    {
        "content": "Delegate to karen to verify base DataTable tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement the base DataTable component",
        "status": "pending",
        "activeForm": "Delegating to ui-developer for base table implementation"
    },
    {
        "content": "Delegate to karen to verify the base DataTable implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to tdd-test-engineer to write tests for sorting functionality",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer for sorting tests"
    },
    {
        "content": "Delegate to karen to verify sorting tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement sorting functionality",
        "status": "pending",
        "activeForm": "Delegating to ui-developer for sorting implementation"
    },
    {
        "content": "Delegate to karen to verify the sorting implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to tdd-test-engineer to write tests for pagination functionality",
        "status": "pending",
        "activeForm": "Delegating to tdd-test-engineer for pagination tests"
    },
    {
        "content": "Delegate to karen to verify pagination tests",
        "status": "pending",
        "activeForm": "Delegating to karen to verify tests"
    },
    {
        "content": "Delegate to ui-developer to implement pagination functionality",
        "status": "pending",
        "activeForm": "Delegating to ui-developer for pagination implementation"
    },
    {
        "content": "Delegate to karen to verify the pagination implementation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify implementation"
    },
    {
        "content": "Delegate to documentation-specialist to document the new DataTable component",
        "status": "pending",
        "activeForm": "Delegating to documentation-specialist to write docs"
    },
    {
        "content": "Delegate to karen to verify the DataTable documentation",
        "status": "pending",
        "activeForm": "Delegating to karen to verify docs"
    },
    {
        "content": "Delegate to code-reviewer to review the complete DataTable component",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## Plan for DataTable Component

1.  **Test/Implement Base Table:** A 4-step process for the basic component.
2.  **Test/Implement Sorting:** A 4-step process for adding sorting.
3.  **Test/Implement Pagination:** A 4-step process for adding pagination.
4.  **Document:** A 2-step process to document the component.
5.  **Code Review:** Final review of all new code.

Do you approve this plan?
"""
    },
    {
        "problem": "Add a dark mode toggle to the UI that persists the user's preference.",
        "solution": """
<sequential-thinking>
This is a full-stack feature involving UI, state management, and a backend endpoint.

1.  **Backend - TDD:** Write tests for a new endpoint `/api/user/preferences` that accepts a theme preference.
    -   Agent: tdd-test-engineer
    -   Verification: karen
2.  **Backend - Implement:** Implement the endpoint to save the user's preference to the database.
    -   Agent: rust-developer
    -   Verification: karen
3.  **Frontend - TDD UI:** Write tests for a new `<ThemeToggle>` component.
    -   Agent: tdd-test-engineer
    -   Verification: karen
4.  **Frontend - Implement UI:** Build the `<ThemeToggle>` component.
    -   Agent: ui-developer
    -   Verification: karen
5.  **Frontend - TDD Logic:** Write tests for the client-side logic that calls the backend and applies the theme.
    -   Agent: tdd-test-engineer
    -   Verification: karen
6.  **Frontend - Implement Logic:** Implement the logic to manage the theme state and call the API.
    -   Agent: ui-developer
    -   Verification: karen
7.  **Code Review:**
    -   Agent: code-reviewer

This is a comprehensive 13-step plan.
</sequential-thinking>
<TodoWrite>
[
    { "content": "Delegate to tdd-test-engineer to write tests for the user preferences API endpoint", "status": "pending", "activeForm": "Delegating tests for preferences API" },
    { "content": "Delegate to karen to verify the user preferences API tests", "status": "pending", "activeForm": "Delegating verification of API tests" },
    { "content": "Delegate to rust-developer to implement the user preferences API endpoint", "status": "pending", "activeForm": "Delegating implementation of preferences API" },
    { "content": "Delegate to karen to verify the user preferences API implementation", "status": "pending", "activeForm": "Delegating verification of API implementation" },
    { "content": "Delegate to tdd-test-engineer to write tests for the ThemeToggle UI component", "status": "pending", "activeForm": "Delegating tests for ThemeToggle UI" },
    { "content": "Delegate to karen to verify the ThemeToggle UI tests", "status": "pending", "activeForm": "Delegating verification of UI tests" },
    { "content": "Delegate to ui-developer to implement the ThemeToggle UI component", "status": "pending", "activeForm": "Delegating implementation of ThemeToggle UI" },
    { "content": "Delegate to karen to verify the ThemeToggle UI implementation", "status": "pending", "activeForm": "Delegating verification of UI implementation" },
    { "content": "Delegate to tdd-test-engineer to write tests for the theme management client logic", "status": "pending", "activeForm": "Delegating tests for client logic" },
    { "content": "Delegate to karen to verify the client logic tests", "status": "pending", "activeForm": "Delegating verification of client logic tests" },
    { "content": "Delegate to ui-developer to implement the theme management client logic", "status": "pending", "activeForm": "Delegating implementation of client logic" },
    { "content": "Delegate to karen to verify the client logic implementation", "status": "pending", "activeForm": "Delegating verification of client logic implementation" },
    { "content": "Delegate to code-reviewer to review the entire dark mode feature", "status": "pending", "activeForm": "Delegating final code review" }
]
</TodoWrite>

## Plan for Dark Mode Feature

1.  **Backend API:** Test and implement the endpoint for saving user preferences (4 steps).
2.  **Frontend UI:** Test and implement the `<ThemeToggle>` switch (4 steps).
3.  **Frontend Logic:** Test and implement the client-side logic for theme management (4 steps).
4.  **Code Review:** Perform a final review of all frontend and backend code.

Do you approve this plan?
"""
    },
    {
        "problem": "Analyze the project's requirements from the PRD and create a task breakdown in Task Master.",
        "solution": """
<sequential-thinking>
The user is asking for a planning operation using Task Master based on a Product Requirements Document (PRD). According to the `Task Master Delegation Protocol`, this complex planning work must be delegated to the `product-strategist`.

1.  **Parse PRD and Create Tasks:** Delegate the entire planning process to the `product-strategist`. This agent will read the PRD, understand the requirements, and use the `taskmaster` tool to create a detailed task breakdown with epics and stories.
    -   Agent: product-strategist
    -   Verification: karen (verify that tasks have been created in Task Master and they align with the PRD).

This is a 2-step delegation. I will not use the `taskmaster` tool directly for this planning operation.
</sequential-thinking>
<TodoWrite>
[
    {
        "content": "Delegate to product-strategist to analyze the PRD and create a complete task breakdown in Task Master",
        "status": "pending",
        "activeForm": "Delegating to product-strategist for project planning"
    },
    {
        "content": "Delegate to karen to verify that the task breakdown in Task Master is complete and accurate based on the PRD",
        "status": "pending",
        "activeForm": "Delegating to karen to verify the project plan"
    }
]
</TodoWrite>

## Plan for Project Task Breakdown

1.  **Delegate Planning:** I will delegate the task of analyzing the PRD and creating the project plan in Task Master to the **product-strategist**.
2.  **Verify Plan:** Afterwards, I will ask **karen** to verify the completeness and accuracy of the generated plan.

Do you approve this plan?
"""
    }
]
