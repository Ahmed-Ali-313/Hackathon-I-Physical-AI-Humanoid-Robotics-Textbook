# ADR-0006: OpenAI Agents SDK Integration for RAG Orchestration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-02-22
- **Feature:** 003-rag-chatbot
- **Context:** Constitution Principle V mandates "OpenAI Agents SDK (chatbot logic and capabilities)" for all agentic logic. Initial architecture used direct API calls (Gemini/OpenAI) with a three-stage RAG pipeline. After analysis, discovered this violated constitution requirements. Need to redesign architecture to use OpenAI Agents SDK as core framework while maintaining dual API support (Gemini primary, OpenAI secondary) for cost optimization. Must preserve RAG grounding, source attribution, and selection-based context mode while adding SDK orchestration layer.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Fundamental change to chatbot architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Direct pipeline, LangChain, custom framework evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all chatbot functionality and conversation management
-->

## Decision

**OpenAI Agents SDK as Core Framework:**
- **Framework**: OpenAI Agents SDK for agent orchestration, tool management, conversation memory
- **Model Configuration**: Dual API support via SDK's custom model configuration
  - Primary: Gemini gemini-1.5-flash (configured via base_url parameter)
  - Secondary: OpenAI gpt-4o-mini (native SDK support)
  - Switching: LLM_PROVIDER environment variable
- **RAG Implementation**: Agent tools pattern (not direct pipeline)
  - Tool 1: `vector_search_tool` - Searches Qdrant for top-5 chunks (threshold 0.7)
  - Tool 2: `retrieve_context_tool` - Formats chunks with source metadata
  - Agent orchestrates: Question → Call vector_search_tool → Call retrieve_context_tool → Generate response
- **System Prompt**: Embedded in agent initialization with tone/pedagogy instructions
- **Selection Mode**: Agent detects selected_text parameter, skips vector search tool

**Architecture Flow:**
```
User Question
    ↓
Agent Service (OpenAI Agents SDK)
    ↓
Agent analyzes question + context
    ↓
[Normal Mode]                    [Selection Mode]
    ↓                                ↓
Calls vector_search_tool         Skips vector search
    ↓                                ↓
Calls retrieve_context_tool      Uses selected_text directly
    ↓                                ↓
Generates response with sources
    ↓
Returns answer + source attribution
```

## Consequences

### Positive

- **Constitution Compliance**: Satisfies Principle V mandate for OpenAI Agents SDK (critical requirement)
- **Orchestration Benefits**: SDK handles tool calling, conversation memory, error handling, retry logic automatically
- **Dual API Support**: SDK's custom model configuration allows Gemini (cost-effective) while using SDK framework
- **Conversation Management**: SDK maintains conversation history across turns without custom implementation
- **Tool Abstraction**: RAG logic encapsulated as reusable tools (vector_search_tool, retrieve_context_tool)
- **Error Handling**: SDK provides built-in error handling for tool failures and API errors
- **Flexibility**: Can add new tools (e.g., calculator, web search) without changing agent core
- **Battle-Tested**: OpenAI's SDK is production-proven with extensive documentation and community support
- **Debugging**: SDK provides structured logging and tool execution traces

### Negative

- **Increased Complexity**: More complex than direct API pipeline (agent + tools vs simple function calls)
- **Learning Curve**: Team must learn OpenAI Agents SDK patterns and tool registration
- **SDK Dependency**: Tightly coupled to OpenAI's agent architecture and tool calling format
- **Potential Vendor Lock-in**: Switching away from SDK requires significant refactoring
- **Abstraction Overhead**: SDK adds layer between code and LLM API (slight latency increase ~50-100ms)
- **Limited Control**: SDK manages orchestration internally (less control over exact execution flow)
- **Gemini Integration**: Requires custom configuration (base_url) since SDK designed for OpenAI models
- **Debugging Complexity**: Tool execution happens inside SDK black box (harder to debug than direct calls)

## Alternatives Considered

**Alternative A: Direct API Pipeline (Original Approach)**
- **Approach**: Three-stage pipeline with direct Gemini/OpenAI API calls (embed → retrieve → generate)
- **Pros**: Simpler, more control, easier to debug, no SDK dependency
- **Cons**: Violates constitution Principle V, no built-in conversation memory, manual error handling
- **Why Rejected**: Constitution mandate for OpenAI Agents SDK is non-negotiable

**Alternative B: LangChain Agents**
- **Approach**: Use LangChain's agent framework with tool calling
- **Pros**: More flexible, supports multiple LLM providers natively, larger ecosystem
- **Cons**: Constitution specifically requires "OpenAI Agents SDK" not LangChain
- **Why Rejected**: Constitution explicitly mandates OpenAI Agents SDK

**Alternative C: Custom Agent Framework**
- **Approach**: Build custom agent orchestration with tool calling from scratch
- **Pros**: Full control, no vendor lock-in, optimized for our use case
- **Cons**: Over-engineering, reinventing the wheel, maintenance burden, doesn't satisfy constitution
- **Why Rejected**: OpenAI SDK is battle-tested; custom framework is unnecessary complexity

**Alternative D: Hybrid Approach (SDK for OpenAI, Direct for Gemini)**
- **Approach**: Use SDK when LLM_PROVIDER=openai, direct API when LLM_PROVIDER=gemini
- **Pros**: Simpler Gemini integration, less abstraction overhead
- **Cons**: Two different code paths, harder to maintain, inconsistent behavior
- **Why Rejected**: SDK supports custom models via base_url; single code path is cleaner

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md) (Phase 0, Section 1)
- Research: [specs/003-rag-chatbot/research.md](../../specs/003-rag-chatbot/research.md) (Section 1: OpenAI Agents SDK Architecture)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Principle V: Tech Stack Compliance)
- Related ADRs:
  - ADR-0002 (LLM and Vector Database Stack) - Defines dual API configuration
  - ADR-0003 (RAG Architecture Pattern) - Extended by this ADR with SDK orchestration layer
- Analysis Report: [history/prompts/003-rag-chatbot/0001-analyze-and-redesign-rag-chatbot-for-sdk-compliance.plan.prompt.md](../../history/prompts/003-rag-chatbot/0001-analyze-and-redesign-rag-chatbot-for-sdk-compliance.plan.prompt.md)
- Official Documentation:
  - [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
  - [OpenAI Agent Custom Models](https://platform.openai.com/docs/agents/custom-models)
  - [OpenAI Agent Tools Guide](https://platform.openai.com/docs/agents/tools)
