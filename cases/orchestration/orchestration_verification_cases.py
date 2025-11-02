"""
Orchestration Verification Cases for CBR MCP Server

Examples: Using karen for verification, quality checking, validation workflows
"""

ORCHESTRATION_VERIFICATION_CASES = [
    {
        "problem": """
Add server-side validation to the user registration endpoint for password strength.
""",
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
""",
        "category": 'orchestration',
        "subcategory": 'verification',
        "tags": ['orchestration', 'verification', 'karen', 'testing', 'validation', 'quality-checking', 'tdd']
    }
]
