# ADR-0002: LLM and Vector Database Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-02-22
- **Feature:** 003-rag-chatbot
- **Context:** Need to implement RAG (Retrieval-Augmented Generation) chatbot that answers student questions using textbook content. Requires LLM for response generation, embeddings for semantic search, and vector database for storing/retrieving textbook chunks. Constitution mandates dual API configuration (Gemini primary, OpenAI secondary) for cost efficiency and flexibility.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core infrastructure for chatbot
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Multiple LLM and vector DB options evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all chatbot functionality
-->

## Decision

**LLM Stack (Dual Configuration):**
- **Primary LLM**: Google Gemini API (gemini-1.5-flash)
- **Secondary LLM**: OpenAI API (gpt-4o-mini)
- **Embeddings**: Google text-embedding-004 (768-dim) or OpenAI text-embedding-3-small
- **Provider Abstraction**: Config-based switching via `LLM_PROVIDER` environment variable

**Vector Database:**
- **Service**: Qdrant Cloud Free Tier
- **Configuration**: 768-dimensional vectors, Cosine distance
- **Chunking Strategy**: 500-1000 tokens per chunk, 100 token overlap, paragraph boundaries
- **Metadata**: Store chapter name, section number, URL, content type with each chunk

**Integration Pattern:**
```python
# Provider abstraction allows switching without code changes
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "openai"

class LLMService:
    def __init__(self):
        if LLM_PROVIDER == "gemini":
            self.client = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
```

## Consequences

### Positive

- **Cost Efficiency**: Gemini free tier provides 15 requests/minute, 1M tokens/day (sufficient for MVP and testing)
- **Flexibility**: Can switch to OpenAI instantly via environment variable if Gemini rate limits hit
- **Performance**: gemini-1.5-flash provides fast responses (<3s typical) suitable for chat
- **Managed Infrastructure**: Qdrant Cloud eliminates vector database management overhead
- **Generous Free Tier**: 1GB storage, 100k vectors sufficient for 17 textbook chapters (~1,000-2,000 chunks)
- **Fast Retrieval**: Sub-500ms search latency for top-5 chunks
- **Constitution Compliance**: Satisfies Principle X requirement for dual API setup
- **Metadata Support**: Qdrant's payload system enables source attribution with clickable links

### Negative

- **Vendor Lock-in**: Switching away from Gemini/Qdrant requires code changes (mitigated by abstraction layer)
- **Rate Limits**: Gemini free tier limited to 15 requests/minute (acceptable for 100 concurrent users)
- **API Stability**: Gemini API is newer, less battle-tested than OpenAI (mitigated by OpenAI fallback)
- **Embedding Compatibility**: Switching between Google and OpenAI embeddings requires re-indexing entire textbook
- **Free Tier Limits**: Qdrant free tier caps at 1GB storage (sufficient for current scope but may need upgrade)
- **Network Dependency**: Both services are cloud-only (no offline mode)

## Alternatives Considered

**Alternative Stack A: OpenAI Only + Pinecone**
- **LLM**: OpenAI (gpt-4o-mini)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Pinecone Free Tier
- **Why Rejected**: Higher costs (OpenAI has no free tier), Pinecone requires credit card for free tier, doesn't satisfy constitution requirement for dual API

**Alternative Stack B: Gemini Only + ChromaDB**
- **LLM**: Google Gemini (gemini-1.5-flash)
- **Embeddings**: Google text-embedding-004
- **Vector DB**: ChromaDB (self-hosted)
- **Why Rejected**: Doesn't satisfy constitution requirement for dual API, ChromaDB requires self-hosting (infrastructure overhead), not cloud-managed

**Alternative Stack C: Multiple LLMs (Gemini + OpenAI + Claude) + Weaviate**
- **LLMs**: Gemini, OpenAI, Claude with load balancing
- **Vector DB**: Weaviate Cloud
- **Why Rejected**: Over-engineering for MVP, increased complexity, Weaviate free tier less generous than Qdrant, managing three LLM providers adds unnecessary overhead

**Alternative Stack D: PostgreSQL pgvector**
- **LLM**: Gemini + OpenAI (same as chosen)
- **Vector DB**: PostgreSQL with pgvector extension (Neon Postgres)
- **Why Rejected**: Lower performance than specialized vector databases, complexity of managing vector indexes, Neon doesn't support pgvector on free tier, sub-optimal for semantic search at scale

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md)
- Research: [specs/003-rag-chatbot/research.md](../../specs/003-rag-chatbot/research.md) (Sections 1, 2)
- Related ADRs: None (first RAG-related ADR)
- Official Documentation:
  - [Google Generative AI Python SDK](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
  - [OpenAI Python SDK](https://platform.openai.com/docs/api-reference/chat)
  - [Qdrant Python Client](https://qdrant.tech/documentation/quick-start/)
  - [Gemini API Pricing](https://ai.google.dev/pricing)
  - [Qdrant Cloud Free Tier](https://qdrant.tech/pricing/)
