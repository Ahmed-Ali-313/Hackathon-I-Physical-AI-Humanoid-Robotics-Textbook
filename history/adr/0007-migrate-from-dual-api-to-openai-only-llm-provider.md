# ADR-0007: Migrate from Dual API to OpenAI-Only LLM Provider

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-02-23
- **Feature:** 004-openai-only
- **Context:** The RAG chatbot was initially designed with dual API provider support (Gemini primary, OpenAI secondary) as mandated by Constitution v2.0.0. However, in practice, only one provider is used at runtime, and managing two API keys adds configuration complexity and maintenance burden. User explicitly requested removal of Gemini configuration to simplify the system. This decision requires amending the constitution from v2.0.0 to v3.0.0 (MAJOR version change) to remove the dual API requirement.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Changes core LLM infrastructure
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Evaluated backward compatibility, deprecation, feature flags
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects embedding service, agent service, config, tests, documentation
-->

## Decision

**LLM Stack (OpenAI-Only):**
- **Chat Completion**: OpenAI gpt-4o-mini (balanced performance/cost for educational chatbot)
- **Embeddings**: OpenAI text-embedding-3-small (768-dimensional, matches existing Qdrant setup)
- **Configuration**: Single environment variable `OPENAI_API_KEY` (removed: `GEMINI_API_KEY`, `LLM_PROVIDER`)
- **Migration Strategy**: Clean removal of all Gemini code, no backward compatibility layer

**Implementation Changes:**
- Remove `google-generativeai` dependency from requirements.txt
- Refactor `embedding_service.py` to OpenAI-only (remove provider parameter and Gemini methods)
- Refactor `agent_service.py` to OpenAI-only (remove provider parameter and Gemini methods)
- Update `config.py` to remove Gemini-related settings
- Update `index_textbook.py` script to use OpenAI embeddings only
- Remove Gemini test cases from unit and integration tests
- Update documentation to reflect OpenAI-only setup

**Vector Embedding Compatibility:**
- Existing Qdrant embeddings compatible if created with OpenAI
- Re-indexing required if embeddings were created with Gemini (check collection metadata)

## Consequences

### Positive

- **Simplified Configuration**: Reduces from 3 environment variables to 1 (`OPENAI_API_KEY` only)
- **Reduced Complexity**: Removes ~500 lines of provider-switching logic from codebase
- **Easier Maintenance**: Single API provider means fewer integration points to maintain
- **Clearer Error Messages**: Explicit OpenAI error handling without fallback confusion
- **Faster Development**: No need to test dual provider scenarios
- **Reduced Dependencies**: Removes `google-generativeai` package
- **Constitution Alignment**: Resolves inconsistency between documented principles and actual usage patterns

### Negative

- **Single Point of Failure**: No fallback provider if OpenAI API is unavailable (mitigated by explicit error messages)
- **Vendor Lock-in**: Switching to another provider requires code changes (acceptable for hackathon project)
- **Rate Limit Risk**: OpenAI free tier has rate limits with no automatic fallback (mitigated by existing rate limiting in code)
- **Potential Re-indexing**: May need to re-index Qdrant embeddings if they were created with Gemini (~10-15 minutes for 17 chapters)
- **Constitution Amendment Required**: Must update constitution.md to v3.0.0 (MAJOR version bump) before merging
- **Breaking Change**: Existing deployments using Gemini will break (acceptable - no production deployments yet)

## Alternatives Considered

**Alternative A: Keep Dual API Support (Status Quo)**
- **Approach**: Maintain both Gemini and OpenAI providers with switching capability
- **Why Rejected**: Adds unnecessary complexity without providing value. Only one provider is used at runtime, managing two API keys increases configuration errors, and Gemini-specific code adds maintenance burden. User explicitly requested simplification.

**Alternative B: Deprecation Path**
- **Approach**: Keep Gemini code but mark as deprecated, remove in future release
- **Why Rejected**: Delays cleanup and adds no value. Since this is a hackathon project with no production deployments, gradual deprecation is unnecessary overhead.

**Alternative C: Feature Flag for Provider Switching**
- **Approach**: Allow runtime switching between providers via environment variable
- **Why Rejected**: Contradicts the goal of simplification. Feature flags add complexity and testing burden. If provider switching is needed in the future, it can be re-implemented with proper justification.

**Alternative D: Migrate to Gemini-Only**
- **Approach**: Remove OpenAI and standardize on Gemini instead
- **Why Rejected**: OpenAI has better documentation, more mature SDK, and wider community support. Gemini API is newer and less battle-tested. OpenAI is the safer choice for production stability.

## References

- Feature Spec: [specs/004-openai-only/spec.md](../../specs/004-openai-only/spec.md)
- Implementation Plan: [specs/004-openai-only/plan.md](../../specs/004-openai-only/plan.md)
- Research: [specs/004-openai-only/research.md](../../specs/004-openai-only/research.md)
- Related ADRs:
  - **SUPERSEDES** [ADR-0002: LLM and Vector Database Stack](./0002-llm-and-vector-database-stack.md) - Removes dual API requirement
- Constitution Amendment: Requires update from v2.0.0 to v3.0.0 (remove Principle V & X dual API mandate)
- Official Documentation:
  - [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
  - [OpenAI Chat Completions](https://platform.openai.com/docs/guides/chat-completions)
  - [OpenAI Error Codes](https://platform.openai.com/docs/guides/error-codes)
