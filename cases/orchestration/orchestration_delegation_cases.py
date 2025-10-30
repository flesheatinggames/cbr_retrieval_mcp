"""
Orchestration Delegation Cases for CBR MCP Server
Examples: Multi-agent coordination, task delegation, workflow handoffs
"""

ORCHESTRATION_DELEGATION_CASES = [
    {
        "problem": "How should I delegate the refactoring of the PaymentProcessor service to use the new StripeClient instead of the legacy BraintreeClient across multiple specialized agents?",
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
        "subcategory": "delegation",
        "tags": [
            "delegation",
            "multi-agent",
            "coordination",
            "workflow",
            "task-assignment",
            "orchestration",
            "tdd",
            "refactoring",
            "agent-handoff",
            "verification"
        ]
    }
]
