# CBR MCP Server - Claude Instructions

## Agent OS Documentation

### Product Context
- **Mission & Vision:** @.agent-os/product/mission.md
- **Technical Architecture:** @.agent-os/product/tech-stack.md
- **Development Roadmap:** @.agent-os/product/roadmap.md
- **Decision History:** @.agent-os/product/decisions.md

### Development Standards
- **Code Style:** @~/.agent-os/standards/code-style.md
- **Best Practices:** @~/.claude/standards/best-practices.md

### Project Management
- **Active Specs:** @.agent-os/specs/
- **Spec Planning:** Use `@.agent-os/instructions/create-spec.md`
- **Tasks Execution:** Use `@.agent-os/instructions/execute-tasks.md`

## Workflow Instructions

When asked to work on this codebase:

1. **First**, check @.agent-os/product/roadmap.md for current priorities
2. **Then**, follow the appropriate instruction file:
   - For new features: @.agent-os/instructions/create-spec.md
   - For tasks execution: @.agent-os/instructions/execute-tasks.md
3. **Always**, adhere to the standards in the files listed above

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- User's specific instructions override (or amend) instructions found in `.agent-os/specs/...`
- Always adhere to established patterns, code style, and best practices documented above.

## Project-Specific Context

This CBR MCP Server is designed for AI agent integration, particularly Claude Code agents. Key considerations:

- **MCP Protocol**: Primary interface for AI agent integration
- **Production Ready**: Comprehensive error handling, monitoring, and async operations
- **Vector Search**: ChromaDB with nomic-ai embeddings for semantic code retrieval
- **Backward Compatibility**: Maintained FastAPI interface during MCP transition

When working on this project, prioritize:
1. MCP protocol compatibility and standards
2. Production reliability and error handling
3. Performance optimization for AI agent use cases
4. Comprehensive testing of all integrations