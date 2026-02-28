# ADR-0008: Translation Architecture and Caching Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-02-28
- **Feature:** 005-urdu-translation
- **Context:** Need to translate 17 textbook chapters from English to Urdu while preserving technical terms, code blocks, and LaTeX equations. Must minimize API costs through caching, handle concurrent translation requests efficiently, and ensure translation quality through automated validation. Target performance: <5s first-time translation, <500ms cached responses, 80%+ cache hit rate.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - establishes translation infrastructure for future language expansion
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - evaluated multiple translation engines, caching strategies, and validation approaches
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - affects backend API, database schema, performance, and cost structure
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement a translation system with the following integrated components:

- **Translation Engine**: OpenAI GPT-4o-mini with structured system prompts for context-aware technical translation
- **Caching Strategy**: PostgreSQL table (`translated_chapters`) with optimistic locking using version field
- **Chunking Strategy**: Semantic chunking by markdown headers (##, ###) for chapters >10,000 words
- **Validation**: Automated structural validation (header count, code blocks, LaTeX equations, markdown parsing)
- **Concurrency Control**: Optimistic locking to avoid holding database locks during long-running API calls

## Consequences

### Positive

- **Cost Efficiency**: Cache-first strategy reduces API costs by 90%+ after initial translations (17 chapters × $0.02 = $0.34 initial cost, then ~$0 for cached requests)
- **Performance**: <500ms cached responses (p95), <5s first-time translations meet user experience requirements
- **Quality Assurance**: Automated validation catches 100% of structural issues (missing code blocks, broken LaTeX) before caching
- **Scalability**: Optimistic locking supports high concurrency without database bottlenecks or timeouts
- **Context Awareness**: GPT-4o-mini with structured prompts preserves technical terms and maintains academic tone
- **Semantic Coherence**: Header-based chunking maintains section context, improving translation quality over arbitrary word-count chunking
- **Future-Proof**: Architecture supports adding more languages (Arabic, Persian) without redesign

### Negative

- **OpenAI Dependency**: Vendor lock-in to OpenAI API; switching translation engines requires prompt re-engineering
- **Cache Invalidation Complexity**: Must track content hashes and implement cleanup jobs for stale/orphaned entries
- **Initial Translation Latency**: 3-5 second wait for first-time translations may frustrate users (mitigated by background pre-translation)
- **Storage Overhead**: ~1MB for 17 cached translations (acceptable but grows with language expansion)
- **Validation Limitations**: Structural validation doesn't catch semantic errors (incorrect translations that are structurally valid)
- **Race Condition Edge Cases**: Optimistic locking may waste API costs if multiple users request same chapter simultaneously (rare but possible)

## Alternatives Considered

### Alternative Translation Engine: Google Translate API
- **Pros**: Cheaper ($20/1M characters vs OpenAI $0.15/$0.60 per 1M tokens), faster responses
- **Cons**: Lacks context awareness, poor technical term preservation, no fine-grained control over translation rules
- **Why Rejected**: Cannot reliably preserve technical terms (ROS 2, VSLAM, URDF) which is a critical requirement

### Alternative Translation Engine: DeepL API
- **Pros**: High translation quality, competitive pricing, good for European languages
- **Cons**: No fine-grained control over term preservation, limited language pairs, no structured prompting
- **Why Rejected**: Cannot guarantee technical term preservation through prompts; less flexible than OpenAI

### Alternative Caching: Redis with TTL
- **Pros**: Faster reads (<1ms), simpler invalidation (TTL-based), no database schema changes
- **Cons**: Volatile storage (data loss on restart), no persistent audit trail, harder to implement optimistic locking
- **Why Rejected**: Need persistent storage for expensive translations; PostgreSQL provides durability and audit trail

### Alternative Concurrency: Pessimistic Locking (Row-Level Locks)
- **Pros**: Guaranteed no race conditions, simpler logic (no version checking)
- **Cons**: Holds database lock for 3-5 seconds during API call, causes contention and timeouts under load
- **Why Rejected**: Unacceptable performance impact; optimistic locking better suited for long-running operations

### Alternative Chunking: Fixed Word Count (2000 words)
- **Pros**: Simpler implementation, predictable chunk sizes, easier progress tracking
- **Cons**: May break mid-sentence or mid-paragraph, loses semantic context, lower translation quality
- **Why Rejected**: Semantic coherence is critical for technical content; header-based chunking maintains context

### Alternative Validation: Manual Review
- **Pros**: Highest quality assurance, catches semantic errors
- **Cons**: Not scalable, slow (hours per chapter), expensive, blocks automated caching
- **Why Rejected**: Impractical for automated system; structural validation catches critical issues while maintaining automation

## References

- Feature Spec: [specs/005-urdu-translation/spec.md](../../specs/005-urdu-translation/spec.md)
- Implementation Plan: [specs/005-urdu-translation/plan.md](../../specs/005-urdu-translation/plan.md)
- Research: [specs/005-urdu-translation/research.md](../../specs/005-urdu-translation/research.md)
- Data Model: [specs/005-urdu-translation/data-model.md](../../specs/005-urdu-translation/data-model.md)
- Related ADRs: ADR-0002 (LLM Stack), ADR-0007 (OpenAI-Only Provider)
- Evaluator Evidence: To be added after implementation and testing
