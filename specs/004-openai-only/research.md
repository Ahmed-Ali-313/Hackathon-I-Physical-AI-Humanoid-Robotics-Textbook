# Research: Migrate RAG Chatbot to OpenAI-Only API

**Feature**: 004-openai-only
**Date**: 2026-02-23
**Status**: Complete

## Research Questions

### Q1: OpenAI API Best Practices for RAG Applications

**Decision**: Use OpenAI text-embedding-3-small for embeddings and gpt-4o-mini for chat completion

**Rationale**:
- **text-embedding-3-small**: Generates 768-dimensional embeddings (matches current Qdrant setup), cost-effective, optimized for semantic search
- **gpt-4o-mini**: Balanced performance/cost ratio, sufficient for educational chatbot use case, supports system prompts for RAG grounding
- Both models are production-ready and well-documented

**Alternatives Considered**:
- **text-embedding-3-large**: Higher quality (3072 dimensions) but requires Qdrant re-indexing and increased storage costs - rejected due to unnecessary complexity
- **gpt-4o**: Higher quality but 10x more expensive than gpt-4o-mini - rejected as overkill for textbook Q&A
- **gpt-3.5-turbo**: Cheaper but lower quality responses - rejected to maintain educational quality standards

**References**:
- OpenAI Embeddings Guide: https://platform.openai.com/docs/guides/embeddings
- OpenAI Chat Completions: https://platform.openai.com/docs/guides/chat-completions

---

### Q2: Migration Strategy - Backward Compatibility

**Decision**: Remove Gemini code entirely, no backward compatibility layer

**Rationale**:
- User explicitly requested removal of Gemini configuration
- No production deployments currently using Gemini (based on constitution stating Gemini as "primary" but OpenAI already implemented)
- Simpler codebase without conditional logic
- Faster migration without maintaining dual code paths

**Alternatives Considered**:
- **Deprecation path**: Keep Gemini code but mark as deprecated - rejected because it delays cleanup and adds no value
- **Feature flag**: Allow runtime switching via environment variable - rejected because it contradicts the goal of simplification
- **Gradual migration**: Phase out Gemini over multiple releases - rejected as unnecessary for a hackathon project

**Migration Steps**:
1. Remove Gemini imports and provider logic from services
2. Update config to remove GEMINI_API_KEY and LLM_PROVIDER
3. Update tests to remove Gemini test cases
4. Remove google-generativeai from requirements.txt
5. Update documentation to reflect OpenAI-only setup

---

### Q3: Vector Embedding Compatibility

**Decision**: Existing Qdrant embeddings are compatible if created with OpenAI; re-indexing required if created with Gemini

**Rationale**:
- Recent commit (91f786c) shows migration from google.generativeai to OpenAI-compatible endpoint for Gemini
- If embeddings were created with Gemini's embedding-001 model, they may have different dimensions or semantic properties
- OpenAI text-embedding-3-small produces consistent 768-dimensional vectors

**Risk Assessment**:
- **Low Risk**: If textbook was indexed with OpenAI embeddings (check Qdrant collection metadata)
- **Medium Risk**: If textbook was indexed with Gemini embeddings (requires re-indexing ~17 chapters)

**Mitigation**:
- Check existing Qdrant collection metadata to determine embedding source
- If Gemini embeddings detected, run `backend/scripts/index_textbook.py` with OpenAI configuration
- Document re-indexing requirement in quickstart.md

**References**:
- Qdrant Collection Info API: https://qdrant.tech/documentation/concepts/collections/
- OpenAI Embedding Dimensions: https://platform.openai.com/docs/guides/embeddings/embedding-models

---

### Q4: Error Handling Without Fallback Provider

**Decision**: Return explicit error messages when OpenAI API fails, no automatic fallback

**Rationale**:
- Removing dual provider means no fallback option
- Better to fail explicitly than silently degrade
- Users can retry or check API status

**Error Scenarios**:
1. **API Key Missing**: Return 500 with "OpenAI API key not configured"
2. **Rate Limit**: Return 429 with "Rate limit exceeded, please try again in X seconds"
3. **API Unavailable**: Return 503 with "OpenAI API temporarily unavailable"
4. **Invalid Request**: Return 400 with specific error from OpenAI

**Implementation**:
- Add try-except blocks in embedding_service.py and agent_service.py
- Map OpenAI error codes to appropriate HTTP status codes
- Log errors for monitoring and debugging

**References**:
- OpenAI Error Codes: https://platform.openai.com/docs/guides/error-codes

---

## Summary

**Key Decisions**:
1. Use OpenAI text-embedding-3-small (768-dim) and gpt-4o-mini
2. Remove all Gemini code without backward compatibility
3. Check and potentially re-index Qdrant embeddings
4. Implement explicit error handling without fallback

**Risks**:
- **Medium**: Qdrant may contain Gemini embeddings requiring re-indexing
- **Low**: OpenAI API rate limits (mitigated by existing rate limiting in code)
- **Low**: Single point of failure (acceptable for hackathon project)

**Next Steps**:
- Phase 1: Design data model changes (minimal - only config changes)
- Phase 1: Document API contracts (unchanged - internal implementation only)
- Phase 1: Create quickstart guide for OpenAI-only setup
