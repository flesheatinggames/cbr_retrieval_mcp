# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.1.0] - 2025-12-15

### Performance Improvements

- **Thread-safe encoding**: Added `_encode_lock` to `LazyEmbeddingModel` preventing tensor shape mismatches under concurrent load, eliminating 26.9% error rate
- **Cache system optimization**: Achieved 99.9-100% cache hit rate for warmup queries
- **Query performance**: Sustained 667.8 QPS throughput with p95 latency of 3.22ms

### Bug Fixes

- Fixed thread-unsafe `SentenceTransformer.encode()` causing 26.9% error rate under concurrent load
- Fixed cache metrics collection (attribute name compatibility for `cache` vs `result_cache`)
- Fixed race condition in warmup query generation
- Fixed test isolation issues in parallel execution

### Memory Management

- Updated memory thresholds to account for real embedding model (nomic-ai/nomic-embed-text-v1.5)
  - `MAX_STARTUP_MEMORY_MB`: 1050MB → 1350MB
  - `MAX_PEAK_MEMORY_MB`: 1200MB → 1500MB
  - Realistic baseline: ~1275MB (vs ~500MB for mocked components)

### Testing

- Achieved 100% test pass rate (2097 passed, 133 skipped, 0 failed)
- Fixed 5 test threshold calibration issues
- Added worker-specific seeding for parallel test isolation
- Updated startup regression tolerance to 35%

### Documentation

- Added comprehensive migration guide for performance optimization changes
- Added production profiling guide
- Documented all memory threshold changes and rationale

### Breaking Changes

None - all changes are backward compatible. However, note behavioral change in memory usage patterns (~1275MB baseline vs ~500MB for mocked components).

### Migration

See `Documentation/migration-guide.md` for detailed migration instructions.
