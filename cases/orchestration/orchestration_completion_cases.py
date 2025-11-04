"""
Orchestration Completion Cases for CBR MCP Server

This module contains cases demonstrating proper orchestration completion workflows:
- Task Completion Protocol execution
- Mandatory Task Completion Gate verification
- Anti-Momentum Safeguard checks
- TodoWrite 100% completion validation
- Blocking authority verification
- Satisfaction Override Mechanism
- Proper completion reporting

These cases show how orchestration workflows properly conclude only after ALL
verification gates have been satisfied and completion authorization granted.
"""

ORCHESTRATION_COMPLETION_CASES = [
    {
        "problem": """
Demonstrate the Mandatory Task Completion Gate verification protocol before marking a parent task complete in tasks.md. Show all 5 verification steps and the authorization decision.
""",
        "solution": """
I have just completed all subtasks for Task 1 (Google Sign-In UI). Before I can mark the parent task complete in tasks.md, I MUST execute the Mandatory Task Completion Gate protocol.

## TASK COMPLETION VERIFICATION AUDIT

**Step 1: TodoWrite Status Check**

<TodoWrite>
[
    {"content": "Delegate to ui-developer to write tests for GoogleSignInButton", "status": "completed", "activeForm": "Delegating to ui-developer for tests"},
    {"content": "Delegate to karen to verify GoogleSignInButton tests", "status": "completed", "activeForm": "Delegating to karen for test verification"},
    {"content": "Delegate to ui-developer to implement GoogleSignInButton", "status": "completed", "activeForm": "Delegating to ui-developer for implementation"},
    {"content": "Delegate to karen to verify GoogleSignInButton implementation", "status": "completed", "activeForm": "Delegating to karen for implementation verification"},
    {"content": "Delegate to code-reviewer for final review", "status": "completed", "activeForm": "Delegating to code-reviewer for final review"}
]
</TodoWrite>

TodoWrite Status: 5 completed, 0 pending ✓
DECISION: Proceed to Step 2

**Step 2: Blocking Authority Verification**

Checking each blocking authority agent:

- ui-developer: requires-karen agent
  - karen response: "VERIFIED COMPLETE" ✓
- code-reviewer: blocking authority agent
  - code-reviewer response: "APPROVED" ✓

All blocking authorities have given positive approval ✓
DECISION: Proceed to Step 3

**Step 3: Satisfaction Recognition Check**

Self-interrogation:
- [ ] Feeling accomplished or satisfied? NO
- [ ] Wanting to summarize progress? NO
- [ ] Thinking "mostly done" or "just a formality"? NO
- [ ] Eager to move on or stop? NO
- [ ] Dismissing remaining steps as minor? NO

NO boxes checked. Satisfaction bias: CLEAR ✓
DECISION: Proceed to Step 4

**Step 4: Final Verification Checklist**

- [x] TodoWrite shows ZERO pending todos? YES
- [x] ALL blocking authority agents have given positive approval? YES
- [x] NO remediation protocols are pending? YES
- [x] ALL subtasks in tasks.md are marked [x]? YES
- [x] I have NOT experienced satisfaction or "close enough" feelings? YES

ALL FIVE ANSWERS = YES ✓
DECISION: Proceed to Step 5

**Step 5: Document Verification**

```
TASK COMPLETION VERIFICATION AUDIT

TodoWrite Status: 5 completed, 0 pending
Blocking Authorities:
  - karen (for ui-developer): VERIFIED COMPLETE
  - code-reviewer: APPROVED
Satisfaction Check: CLEAR
Final Checklist: 5/5 YES

AUTHORIZATION: GRANTED
```

## Authorization Granted

I am now authorized to mark Task 1 complete in tasks.md:

<tool_code>
    <tool name="Edit">
        <file_path>.agent-os/specs/2025-03-15-google-signin/tasks.md</file_path>
        <old_string>- [ ] 1. Google Sign-In UI Component</old_string>
        <new_string>- [x] 1. Google Sign-In UI Component</new_string>
    </tool>
</tool_code>

Task 1 is now marked complete. I will proceed to check if any other tasks remain before announcing overall completion.
""",
        "category": "orchestration",
        "subcategory": "completion",
        "tags": [
            "orchestration",
            "completion",
            "mandatory-completion-gate",
            "verification-audit",
            "authorization",
            "blocking-authorities",
        ],
    }
]
