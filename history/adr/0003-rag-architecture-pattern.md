# ADR-0003: RAG Architecture Pattern

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Superseded by ADR-0006 (OpenAI Agents SDK Integration)
- **Date:** 2026-02-22
- **Feature:** 003-rag-chatbot
- **Context:** Need to implement RAG pipeline that ensures chatbot responses are grounded in textbook content, not general LLM knowledge. Constitution Principle X mandates strict RAG grounding with 0.7 confidence threshold, source attribution, selection-based context mode, and explicit uncertainty handling. Must balance answer quality with response speed (<5 seconds for 90% of queries).

**Note:** This ADR described the original three-stage pipeline approach. After constitution compliance analysis, the architecture was redesigned to use OpenAI Agents SDK with agent tools pattern (see ADR-0006). The core RAG principles (grounding, source attribution, uncertainty handling) remain the same, but implementation changed from direct pipeline to SDK-orchestrated tools.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines core chatbot behavior
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Multi-hop, re-ranking, hybrid search evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all question-answering functionality
-->

## Decision

**Three-Stage RAG Pipeline:**
1. **Embed Question**: Generate 768-dim embedding using Google text-embedding-004 or OpenAI text-embedding-3-small
2. **Retrieve Context**: Search Qdrant for top-5 chunks with 0.7 minimum confidence threshold
3. **Generate Response**: Use retrieved context with LLM (Gemini/OpenAI) to generate grounded answer

**Key Parameters:**
- **Top-K**: 5 chunks retrieved per query
- **Confidence Threshold**: 0.7 minimum (per constitution)
- **Prompt Template**: Explicit instruction to use ONLY provided textbook content
- **Source Attribution**: Extract chapter/section/URL from chunk metadata for clickable links

**Selection-Based Context Mode:**
- When user has text selected: Skip retrieval (Stage 2), use selected text directly as context
- Still include source attribution from selection metadata
- Enables precise, context-aware help for complex passages

**Uncertainty Handling:**
- If no chunks meet 0.7 threshold: Return "I don't have information about this in the textbook"
- Suggest related topics that ARE covered in textbook
- Never hallucinate facts about Physical AI, robotics, or course topics

## Consequences

### Positive

- **Grounding**: Ensures responses based on textbook content, not general LLM knowledge
- **Source Attribution**: Retrieved chunks include metadata for clickable source links (satisfies FR-011, FR-012)
- **Confidence Threshold**: 0.7 threshold prevents low-quality matches, reduces hallucinations
- **Simplicity**: Straightforward pipeline without complex re-ranking or multi-hop retrieval (faster, easier to debug)
- **Selection Mode**: Enables precise help for complex passages without full textbook search
- **Explicit Uncertainty**: Clear "I don't have information" responses when content not found (satisfies FR-017)
- **Fast Performance**: Single retrieval step keeps latency low (<500ms for vector search)
- **Constitution Compliance**: Satisfies all 5 RAG architecture subsections (Principle X)

### Negative

- **Single-Hop Limitation**: Cannot answer questions requiring information from multiple disparate sections
- **No Re-Ranking**: Relies solely on Qdrant's cosine similarity (may miss relevant chunks with different phrasing)
- **Fixed Top-K**: Always retrieves 5 chunks (may be too many for simple questions, too few for complex ones)
- **Threshold Rigidity**: 0.7 threshold may reject valid matches with slight semantic differences
- **Context Window**: Limited to 5 chunks (~2,500-5,000 tokens), may not capture full context for complex topics
- **No Query Expansion**: Doesn't handle synonyms or alternative phrasings (relies on embedding similarity)

## Alternatives Considered

**Alternative A: Multi-Hop RAG**
- **Approach**: Retrieve initial chunks, identify gaps, retrieve additional chunks iteratively
- **Why Rejected**: Over-engineering for textbook Q&A (single retrieval sufficient for most questions), adds latency (2-3x slower), increased complexity for debugging, textbook content is well-structured (doesn't require multi-hop)

**Alternative B: Re-Ranking with Cross-Encoder**
- **Approach**: Retrieve top-20 chunks, re-rank with cross-encoder model, select top-5
- **Why Rejected**: Adds 200-300ms latency, requires additional model deployment, Qdrant's cosine similarity sufficient for well-structured textbook content, increased complexity

**Alternative C: Hybrid Search (Vector + Keyword)**
- **Approach**: Combine vector search with BM25 keyword search, merge results
- **Why Rejected**: Textbook content is well-structured and semantic (vector search sufficient), adds complexity, Qdrant doesn't natively support hybrid search (would require custom implementation)

**Alternative D: Agentic RAG with Tool Use**
- **Approach**: LLM decides when to retrieve, what to retrieve, and can use multiple tools
- **Why Rejected**: Out of scope for MVP, significantly increased complexity, higher latency, harder to debug, constitution requires predictable grounding behavior

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md) (FR-010 to FR-019)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md)
- Research: [specs/003-rag-chatbot/research.md](../../specs/003-rag-chatbot/research.md) (Section 3)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Principle X)
- Related ADRs: ADR-0002 (LLM and Vector Database Stack)
- Official Documentation:
  - [RAG Best Practices (OpenAI)](https://platform.openai.com/docs/guides/prompt-engineering/strategy-use-external-tools)
  - [Qdrant Semantic Search Tutorial](https://qdrant.tech/documentation/tutorials/search-beginners/)
