# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/spec.md

> Created: 2025-10-27
> Status: Ready for Implementation

## Tasks

- [x] 1. Create Migration Script and Category Detection Logic
  - [x] 1.1 Write tests for MetadataMigration.detect_category_subcategory method (all category patterns)
  - [x] 1.2 Write tests for MetadataMigration.extract_tags method
  - [x] 1.3 Implement MetadataMigration class with pattern matching logic
  - [x] 1.4 Implement detect_category_subcategory with regex patterns for all categories
  - [x] 1.5 Implement extract_tags with technology keyword detection
  - [x] 1.6 Write tests for migrate_collection method
  - [x] 1.7 Implement migrate_collection method with ChromaDB update logic
  - [x] 1.8 Verify all migration unit tests pass

- [x] 2. Update ProductionCBRRetriever for Category Filtering
  - [x] 2.1 Write tests for search_by_category with category-only filtering
  - [x] 2.2 Write tests for search_by_category with category+subcategory filtering
  - [x] 2.3 Write tests for search_by_category with query text
  - [x] 2.4 Write tests for search_by_category error handling (invalid category, ChromaDB errors)
  - [x] 2.5 Implement enhanced search_by_category method with ChromaDB where filters
  - [x] 2.6 Add category validation logic (VALID_CATEGORIES constant)
  - [x] 2.7 Implement fallback logic for ChromaDB query errors
  - [x] 2.8 Verify all search_by_category tests pass

- [x] 3. Update get_categories for Hierarchical Structure
  - [x] 3.1 Write tests for get_categories hierarchical structure
  - [x] 3.2 Write tests for get_categories with counts per category/subcategory
  - [x] 3.3 Write tests for get_categories with empty collection
  - [x] 3.4 Implement new get_categories method with ChromaDB aggregation
  - [x] 3.5 Build hierarchical category structure with subcategory counts
  - [x] 3.6 Verify all get_categories tests pass

- [x] 4. Create Migration Script CLI
  - [x] 4.1 Write integration tests for full collection migration
  - [x] 4.2 Write integration tests for idempotent migration
  - [x] 4.3 Write integration tests for partial migration completion
  - [x] 4.4 Create migrate_metadata.py script with CLI interface
  - [x] 4.5 Implement main() function with ChromaDB connection and migration execution
  - [x] 4.6 Add progress reporting and summary output
  - [x] 4.7 Add validation check after migration completes
  - [x] 4.8 Verify all migration integration tests pass

- [x] 5. Test Category Filtering End-to-End
  - [x] 5.1 Write integration tests for category-only filtering
  - [x] 5.2 Write integration tests for category+subcategory filtering
  - [x] 5.3 Write integration tests for backward compatibility (no filter)
  - [x] 5.4 Create test collection with diverse categories
  - [x] 5.5 Execute category filtering queries and verify results
  - [x] 5.6 Execute backward compatibility queries and verify no regression
  - [x] 5.7 Verify all category filtering integration tests pass

- [x] 6. Update MCP Tools for Category Parameters
  - [x] 6.1 Write tests for cbr_search_category tool with new parameters
  - [x] 6.2 Write tests for cbr_retrieve tool backward compatibility
  - [x] 6.3 Update cbr_search_category MCP tool to accept subcategory parameter
  - [x] 6.4 Update tool parameter validation and documentation
  - [x] 6.5 Verify cbr_retrieve tool unchanged (backward compatibility)
  - [x] 6.6 Verify all MCP tool tests pass

- [x] 7. Performance and Validation Testing
  - [x] 7.1 Write performance tests for category filtering (1000 case collection)
  - [x] 7.2 Write performance tests for migration script
  - [x] 7.3 Write validation tests for metadata completeness
  - [x] 7.4 Write validation tests for subcategory-category consistency
  - [x] 7.5 Execute performance tests and verify < 200ms response times
  - [x] 7.6 Execute validation tests on migrated collection
  - [x] 7.7 Create validation helper script for metadata integrity checks
  - [x] 7.8 Verify all performance and validation tests pass

- [x] 8. Documentation and Migration Guide
  - [x] 8.1 Document new category taxonomy in README
  - [x] 8.2 Document migration script usage and options
  - [x] 8.3 Document enhanced MCP tool parameters
  - [x] 8.4 Create migration runbook for production deployment
  - [x] 8.5 Update MCP tool examples with category filtering
  - [x] 8.6 Add troubleshooting guide for migration issues
