"""
Orchestration Completion Cases for CBR MCP Server

This module contains cases demonstrating proper orchestration completion workflows:
- Subtask Completion Ritual execution
- Mandatory Task Completion Gate verification (for Parent Tasks)
- Successful and Failed completion audits
- Parallel plan completion
- Anti-Momentum Safeguard checks
- TodoWrite 100% completion validation
- Blocking authority verification
"""

ORCHESTRATION_COMPLETION_CASES = [
    {
        "problem": """
Demonstrate the Mandatory Task Completion Gate verification protocol for a *Sequential Task* (`last_login_ip`) before marking the parent task complete in our task system.
""",
        "solution": """
All subtasks for Task 2 (Add last_login_ip) are complete. Before I can mark the parent task complete, I MUST execute the Mandatory Task Completion Gate protocol.

As per the Subtask Completion Ritual (Step 0), I must first search for completion examples.

<thinking>
I am about to run the Mandatory Task Completion Gate. First, I must search for examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration completion mandatory task gate</query>
        <category>orchestration</category>
        <subcategory>completion</subcategory>
    </tool>
</tool_code>
<thinking>
I have reviewed the completion examples. I will now execute the 5-step verification audit.
</thinking>

## TASK COMPLETION VERIFICATION AUDIT

**Step 1: TodoWrite Status Check**

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
My TodoWrite list shows all 7 tasks for this feature. I will now check their status.
[
    "Write Repository Tests: tdd-test-engineer" (completed),
    "Verify Tests: karen" (completed),
    "Update Code: rust-developer" (completed),
    "Verify Code: karen" (completed),
    "Write Migration Script: aws-devops-engineer" (completed),
    "Verify Migration Script: karen" (completed),
    "Final Code Review: code-reviewer" (completed)
]
</thinking>

TodoWrite Status: 7 completed, 0 pending ✓
DECISION: Proceed to Step 2

**Step 2: Blocking Authority Verification**

Checking each blocking authority agent involved in this plan:
- karen (for tdd-test-engineer): "VERIFIED COMPLETE" ✓
- karen (for rust-developer): "VERIFIED COMPLETE" ✓
- karen (for aws-devops-engineer): "VERIFIED COMPLETE" ✓
- code-reviewer: "APPROVED" ✓

All blocking authorities have given positive approval ✓
DECISION: Proceed to Step 3

**Step 3: Satisfaction Recognition Check**

Self-interrogation:
- [ ] Feeling accomplished or satisfied? NO
- [ ] Wanting to summarize progress? NO
- [ ] Thinking "mostly done" or "just a formality"? NO

Satisfaction bias: CLEAR ✓
DECISION: Proceed to Step 4

**Step 4: Final Verification Checklist**

- [x] TodoWrite shows ZERO pending todos? YES
- [x] ALL blocking authority agents have given positive approval? YES
- [x] NO remediation protocols are pending? YES
- [x] ALL subtasks in the task list are marked [x]? YES
- [x] I have NOT experienced satisfaction or "close enough" feelings? YES

ALL FIVE ANSWERS = YES ✓
DECISION: Proceed to Step 5

**Step 5: Document Verification**

```
TASK COMPLETION VERIFICATION AUDIT

TodoWrite Status: 7 completed, 0 pending
Blocking Authorities:
  - karen (for tdd-test-engineer): VERIFIED COMPLETE
  - karen (for rust-developer): VERIFIED COMPLETE
  - karen (for aws-devops-engineer): VERIFIED COMPLETE
  - code-reviewer: APPROVED
Satisfaction Check: CLEAR
Final Checklist: 5/5 YES

AUTHORIZATION: GRANTED
```

## Authorization Granted

I am now authorized to mark Task 2 as complete:

<tool_code>
    <tool name="UpdateTaskStatus">
        <task_id>task_2</task_id>
        <parent_task>2. Add last_login_ip field</parent_task>
        <new_status>complete</new_status>
    </tool>
</tool_code>

Task 2 is now marked complete.
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
            "cbr-retrieval",
            "ritual",
            "sequential",
            "agnostic",
        ],
    },
    {
        "problem": """
Demonstrate the Mandatory Task Completion Gate for a *Parallel Task* (`Google Sign-In`) before marking the parent task complete.
""",
        "solution": """
All subtasks for Task 1 (Google Sign-In) are complete. This task had parallel tracks (UI and Backend). I must now execute the Mandatory Task Completion Gate protocol.

<thinking>
I am about to run the Mandatory Task Completion Gate for a parallel plan. First, I must search for examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration completion parallel plan</query>
        <category>orchestration</category>
        <subcategory>completion</subcategory>
    </tool>
</tool_code>
<thinking>
I have reviewed the completion examples. I will now execute the 5-step verification audit.
</thinking>

## TASK COMPLETION VERIFICATION AUDIT

**Step 1: TodoWrite Status Check**

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
My TodoWrite list shows all 5 tasks for this feature. I will now check their status.
[
    "Create UI Component: ui-developer" (completed),
    "Verify UI Component: karen" (completed),
    "Create Backend Function: firebase-backend-architect" (completed),
    "Verify Backend Function: karen" (completed),
    "Final Code Review: code-reviewer" (completed)
]
</thinking>

TodoWrite Status: 5 completed, 0 pending ✓
DECISION: Proceed to Step 2

**Step 2: Blocking Authority Verification**

Checking all blocking authority agents involved in this parallel plan:
- *Track A (UI):*
  - karen (for ui-developer): "VERIFIED COMPLETE" ✓
- *Track B (Backend):*
  - karen (for firebase-backend-architect): "VERIFIED COMPLETE" ✓
- *Join Phase:*
  - code-reviewer: "APPROVED" ✓

All blocking authorities have given positive approval ✓
DECISION: Proceed to Step 3

**Step 3: Satisfaction Recognition Check**

Satisfaction bias: CLEAR ✓
DECISION: Proceed to Step 4

**Step 4: Final Verification Checklist**

- [x] TodoWrite shows ZERO pending todos? YES
- [x] ALL blocking authority agents have given positive approval? YES
- [x] NO remediation protocols are pending? YES
- [x] ALL subtasks in the task list are marked [x]? YES
- [x] I have NOT experienced satisfaction or "close enough" feelings? YES

ALL FIVE ANSWERS = YES ✓
DECISION: Proceed to Step 5

**Step 5: Document Verification**

```
TASK COMPLETION VERIFICATION AUDIT

TodoWrite Status: 5 completed, 0 pending
Blocking Authorities:
  - karen (Track A): VERIFIED COMPLETE
  - karen (Track B): VERIFIED COMPLETE
  - code-reviewer (Join): APPROVED
Satisfaction Check: CLEAR
Final Checklist: 5/5 YES

AUTHORIZATION: GRANTED
```

## Authorization Granted

I am now authorized to mark Task 1 as complete:

<tool_code>
    <tool name="UpdateTaskStatus">
        <task_id>task_1</task_id>
        <parent_task>1. Google Sign-In Feature</parent_task>
        <new_status>complete</new_status>
    </tool>
</tool_code>

Task 1 is now marked complete.
""",
        "category": "orchestration",
        "subcategory": "completion",
        "tags": [
            "orchestration",
            "completion",
            "mandatory-completion-gate",
            "parallel",
            "blocking-authorities",
            "cbr-retrieval",
            "ritual",
            "agnostic",
        ],
    },
    {
        "problem": """
Demonstrate a *Failed* Mandatory Task Completion Gate due to a pending todo.
""",
        "solution": """
I have just completed the verification of the Dark Mode logic (Step 12) and believe the task is complete. I will now execute the Mandatory Task Completion Gate protocol before marking the parent task complete.

<thinking>
I am about to run the Mandatory Task Completion Gate. First, I must search for examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration completion failed audit</query>
        <category>orchestration</category>
        <subcategory>completion</subcategory>
    </tool>
</tool_code>
<thinking>
I have reviewed the completion examples. I will now execute the 5-step verification audit.
</thinking>

## TASK COMPLETION VERIFICATION AUDIT

**Step 1: TodoWrite Status Check**

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
My TodoWrite list shows 13 tasks for this feature. I will now check their status.
[
    "Backend API Tests: tdd-test-engineer" (completed),
    "Verify API Tests: karen" (completed),
    "Backend API Implementation: firebase-backend-architect" (completed),
    "Verify API Implementation: karen" (completed),
    "Frontend UI Tests: tdd-test-engineer" (completed),
    "Verify UI Tests: karen" (completed),
    "Frontend UI Implementation: ui-developer" (completed),
    "Verify UI Implementation: karen" (completed),
    "Frontend Logic Tests: tdd-test-engineer" (completed),
    "Verify Logic Tests: karen" (completed),
    "Frontend Logic Implementation: ui-developer" (completed),
    "Verify Logic Implementation: karen" (completed),
    "Code Review: code-reviewer" (pending)
]
</thinking>

TodoWrite Status: 12 completed, 1 pending ✗
DECISION: STOP. You are FORBIDDEN from marking complete.

**Step 2: Blocking Authority Verification**
N/A - Stopped at Step 1.

**Step 3: Satisfaction Recognition Check**
N/A - Stopped at Step 1.

**Step 4: Final Verification Checklist**
- [ ] TodoWrite shows ZERO pending todos? NO ✗

**Step 5: Document Verification**

```
TASK COMPLETION VERIFICATION AUDIT

TodoWrite Status: 12 completed, 1 pending
Blocking Authorities: [Verification Halted]
Satisfaction Check: [Verification Halted]
Final Checklist: 0/5 YES

AUTHORIZATION: DENIED
```

## Authorization Denied

Authorization to mark the parent task complete is **DENIED**.
Reason: The `TodoWrite` check revealed 1 pending task: "Code Review: code-reviewer".
My "Satisfaction Override Mechanism" has been triggered. My feeling of completion was a psychological trap.

I will now proceed to the next pending todo, which is delegating to the `code-reviewer`.
""",
        "category": "orchestration",
        "subcategory": "completion",
        "tags": [
            "orchestration",
            "completion",
            "mandatory-completion-gate",
            "failed-audit",
            "satisfaction-override",
            "anti-momentum",
            "cbr-retrieval",
            "ritual",
            "agnostic",
        ],
    },
    {
        "problem": """
Demonstrate the simple `Subtask Completion Ritual` after one subtask (e.g., implementing UI) is verified by `karen`.
""",
        "solution": """
`karen` has just returned "VERIFIED COMPLETE" for subtask 1.1 (Implement `GoogleSignInButton`).
I must now execute the `Subtask Completion Ritual`.

**Step 0: Search CBR**

<thinking>
As per my Subtask Completion Ritual (Step 0), I must first search for completion examples.
</thinking>
<tool_code>
    <tool name="cbr-retrieval" alias="cbr-mcp">
        <query>orchestration completion subtask ritual</query>
        <category>orchestration</category>
        <subcategory>completion</subcategory>
    </tool>
</tool_code>
<thinking>
I have reviewed the completion examples. I will now proceed with the ritual.
</thinking>

**Step 1: Update Subtask in Task System**

<tool_code>
    <tool name="UpdateTaskStatus">
        <subtask_id>subtask_1.1</subtask_id>
        <parent_task_id>task_1</parent_task_id>
        <description>1.1 Implement `GoogleSignInButton`</description>
        <new_status>complete</new_status>
    </tool>
</tool_code>

**Step 2: Check for Overall Completion**

<tool_code>
    <tool name="GetTaskStatus">
        <parent_task_id>task_1</parent_task_id>
    </tool>
</tool_code>

<thinking>
I have checked the status of the parent task. The status is:
- [x] 1.1 Implement `GoogleSignInButton`
- [ ] 1.2 Implement `handleGoogleAuthToken`
- [ ] 1.3 Final Code Review

Not all subtasks for Parent Task 1 are complete.
</thinking>

**Step 3: Report or Proceed**

Subtasks remain. I will now proceed to the next pending subtask, which is delegating the implementation of `handleGoogleAuthToken` (subtask 1.2). I will not comment to the user at this time, as the workflow is ongoing.
""",
        "category": "orchestration",
        "subcategory": "completion",
        "tags": [
            "orchestration",
            "completion",
            "subtask-completion-ritual",
            "workflow",
            "anti-momentum",
            "cbr-retrieval",
            "ritual",
            "agnostic",
        ],
    }
]