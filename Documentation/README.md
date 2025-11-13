# CBR MCP Server Documentation

> Last Updated: 2025-11-13
> Version: 1.0.0

## Documentation Index

This directory contains comprehensive guides for operating and maintaining the CBR MCP Server.

### Migration Guides

**Choose the right migration guide for your needs:**

| Guide | Purpose | When to Use |
|-------|---------|-------------|
| [MIGRATION.md](./MIGRATION.md) | Case Base Structure Migration | Migrating from monolithic case_base.py to modular cases/ directory structure |
| [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) | Metadata Enhancement Migration | Initial deployment of category/subcategory/tags metadata feature (Oct 2025) |
| [Database-Migration-Guide.md](./Database-Migration-Guide.md) | Metadata Storage Bug Fix | Fixing metadata storage bug where categories weren't persisted to database (Nov 2025) |

**Migration Order:** If you're migrating from an older installation, apply migrations in the order listed above.

### Configuration & Setup

- **[CBR-MCP-Server-Configuration-Guide.md](./CBR-MCP-Server-Configuration-Guide.md)** - Complete server configuration reference
- **[deployment-guide.md](./deployment-guide.md)** - Production deployment procedures and best practices
- **[Metadata-Schema-Guide.md](./Metadata-Schema-Guide.md)** - Metadata schema reference and usage guidelines

### Monitoring & Operations

- **[Health-Dashboard-Guide.md](./Health-Dashboard-Guide.md)** - Local health dashboard usage and metrics interpretation
- **[monitoring-setup-guide.md](./monitoring-setup-guide.md)** - Setting up production monitoring and alerting
- **[performance-tuning-guide.md](./performance-tuning-guide.md)** - Performance optimization strategies and tuning parameters
- **[troubleshooting-guide.md](./troubleshooting-guide.md)** - Common issues and resolution procedures

## Quick Links

### For New Users
1. Start with [deployment-guide.md](./deployment-guide.md)
2. Configure using [CBR-MCP-Server-Configuration-Guide.md](./CBR-MCP-Server-Configuration-Guide.md)
3. Set up monitoring with [monitoring-setup-guide.md](./monitoring-setup-guide.md)

### For Existing Users
1. Check if migrations are needed (see Migration Guides table above)
2. Optimize performance with [performance-tuning-guide.md](./performance-tuning-guide.md)
3. Monitor health with [Health-Dashboard-Guide.md](./Health-Dashboard-Guide.md)

### For Troubleshooting
1. Start with [troubleshooting-guide.md](./troubleshooting-guide.md)
2. Check [Health-Dashboard-Guide.md](./Health-Dashboard-Guide.md) for system metrics
3. Review [Metadata-Schema-Guide.md](./Metadata-Schema-Guide.md) if experiencing search issues

## Getting Help

- **GitHub Issues**: https://github.com/anthropics/cbr_retrieval_mcp/issues
- **Documentation Updates**: Submit PRs to improve these guides
