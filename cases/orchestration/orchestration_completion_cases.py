"""
Orchestration Completion Cases for CBR MCP Server

This module contains cases demonstrating orchestration completion workflows:
- Task completion verification and reporting
- Workflow finalization procedures
- Summary generation and user communication
- TodoWrite completion tracking

These cases show how orchestration workflows properly conclude after all
subtasks have been verified and completed.
"""

ORCHESTRATION_COMPLETION_CASES = [
    {
        "problem": "After karen verifies that the LoginButton component implementation is complete, how do I properly finalize the workflow and report completion to the user?",
        "solution": """
<thinking>
Karen has just responded with "VERIFIED COMPLETE" for the LoginButton component. According to the Task Completion Protocol, I must now:

1. Update the subtask in Agent OS tasks.md from `- [ ]` to `- [x]`
2. Re-read the entire tasks.md to check if ALL subtasks are complete
3. Update TodoWrite to mark the current todo as complete
4. Check if ALL todos in TodoWrite are complete
5. If everything is complete: announce completion to the user
6. If work remains: proceed to the next pending todo without comment
</thinking>

**Step 1: Update Subtask in Agent OS**
I will read the tasks.md file and update the just-completed subtask:
- From: `- [ ] 1.2 Implement the LoginButton component`
- To: `- [x] 1.2 Implement the LoginButton component`

**Step 2: Check Overall Completion**
After updating, I re-read the entire tasks.md file and see:
- [x] 1.1 Write tests for the LoginButton component
- [x] 1.2 Implement the LoginButton component
- [x] 1.3 Verify all tests pass
- [ ] 1.4 Create documentation for the LoginButton component
- [ ] 1.5 Final code review

Result: NOT all subtasks are complete (1.4 and 1.5 remain).

**Step 3: Update TodoWrite**
<TodoWrite>
[
    {
        "content": "Delegate to ui-developer to write tests for the LoginButton component",
        "status": "completed",
        "activeForm": "Delegating to ui-developer for tests"
    },
    {
        "content": "Delegate to karen to verify the LoginButton tests",
        "status": "completed",
        "activeForm": "Delegating to karen for test verification"
    },
    {
        "content": "Delegate to ui-developer to implement the LoginButton component",
        "status": "completed",
        "activeForm": "Delegating to ui-developer for implementation"
    },
    {
        "content": "Delegate to karen to verify the LoginButton implementation",
        "status": "completed",
        "activeForm": "Delegating to karen for implementation verification"
    },
    {
        "content": "Delegate to documentation-specialist to create component documentation",
        "status": "pending",
        "activeForm": "Delegating to documentation-specialist for docs"
    },
    {
        "content": "Delegate to code-reviewer for final review",
        "status": "pending",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

**Step 4: Determine Next Action**
Since there are still pending todos (documentation and code review), I will proceed directly to the next pending todo without announcing completion.

I will now delegate the next task to the documentation-specialist.

---

**ALTERNATE SCENARIO: All Work Complete**

If instead ALL subtasks were marked `- [x]` and ALL TodoWrite items were marked "completed":

<TodoWrite>
[
    {
        "content": "Delegate to ui-developer to write tests for the LoginButton component",
        "status": "completed",
        "activeForm": "Delegating to ui-developer for tests"
    },
    {
        "content": "Delegate to karen to verify the LoginButton tests",
        "status": "completed",
        "activeForm": "Delegating to karen for test verification"
    },
    {
        "content": "Delegate to ui-developer to implement the LoginButton component",
        "status": "completed",
        "activeForm": "Delegating to ui-developer for implementation"
    },
    {
        "content": "Delegate to karen to verify the LoginButton implementation",
        "status": "completed",
        "activeForm": "Delegating to karen for implementation verification"
    },
    {
        "content": "Delegate to documentation-specialist to create component documentation",
        "status": "completed",
        "activeForm": "Delegating to documentation-specialist for docs"
    },
    {
        "content": "Delegate to code-reviewer for final review",
        "status": "completed",
        "activeForm": "Delegating to code-reviewer for final review"
    }
]
</TodoWrite>

## ✅ LoginButton Component Complete

The LoginButton component has been successfully implemented and verified. All planned work is complete:

### Completed Work
1. **Tests Written** - Comprehensive test suite created and verified by karen
2. **Component Implemented** - LoginButton component built and verified by karen
3. **Documentation Created** - Component documentation written and verified
4. **Code Reviewed** - Final code review passed by code-reviewer

### Summary
The LoginButton component is ready for production use. All tests pass, documentation is complete, and code quality has been verified.

The entire task is now complete. Is there anything else you'd like me to work on?
""",
        "category": "orchestration",
        "subcategory": "completion",
        "tags": [
            "orchestration",
            "completion",
            "workflow",
            "tasks",
            "summary",
            "finalization",
            "TodoWrite",
            "reporting",
            "task-completion-protocol",
            "verification-complete"
        ]
    }
    
]
