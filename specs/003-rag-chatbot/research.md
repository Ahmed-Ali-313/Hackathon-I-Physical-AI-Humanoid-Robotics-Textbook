# Research: RAG Chatbot Integration

**Feature**: 003-rag-chatbot
**Date**: 2026-02-22 (Revised for OpenAI Agents SDK with dual API support)
**Purpose**: Document technical research and decisions for RAG chatbot implementation

## 1. OpenAI Agents SDK Architecture with Dual API Support (Constitution-Mandated)

### Decision
Use OpenAI Agents SDK as the core framework for all agentic logic, tool orchestration, and conversation management, configured to support both Gemini (primary) and OpenAI (secondary) models through the chat completion interface.

### Rationale
- **Constitution Compliance**: Principle V mandates "OpenAI Agents SDK (chatbot logic and capabilities)"
- **Cost Optimization**: Gemini offers generous free tier (15 req/min, 1M tokens/day) while maintaining SDK benefits
- **Flexibility**: Can switch between providers via configuration without code changes
- **SDK Compatibility**: OpenAI Agents SDK supports any model with chat completion interface, including Gemini
- **Best of Both Worlds**: SDK orchestration + cost-effective Gemini models

### Implementation Pattern
```python
# config.py
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "openai"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# agent_service.py
from openai_agents import Agent, Tool

class AgentService:
    def __init__(self):
        # Configure model based on provider
        if LLM_PROVIDER == "gemini":
            model_config = {
                "model": "gemini-1.5-flash",
                "api_key": GEMINI_API_KEY,
                "base_url": "https://generativelanguage.googleapis.com/v1beta"  # Gemini endpoint
            }
        else:
            model_config = {
                "model": "gpt-4o-mini",
                "api_key": OPENAI_API_KEY
            }

        # Initialize agent with configured model
        self.agent = Agent(
            **model_config,
            tools=[vector_search_tool, retrieve_context_tool],
            system_prompt="""You are a helpful teaching assistant for a Physical AI textbook.
            Only answer questions using the provided context from the textbook.
            If the context is insufficient, state 'I don't have information about this in the textbook'
            and suggest related topics that ARE covered."""
        )

    async def process_question(self, question: str, selected_text: str = None) -> dict:
        if selected_text:
            context = {"selected_text": selected_text}
        else:
            context = {}

        response = await self.agent.run(
            user_message=question,
            context=context
        )

        return {
            "answer": response.content,
            "sources": response.tool_results.get("sources", []),
            "confidence": response.tool_results.get("confidence", 0.0)
        }
```

### Agent Tools
1. **vector_search_tool**: Searches Qdrant for relevant textbook chunks (top-5, threshold 0.7)
2. **retrieve_context_tool**: Formats retrieved chunks with source metadata for agent

### Model Comparison

| Feature | Gemini (Primary) | OpenAI (Secondary) |
|---------|------------------|-------------------|
| Model | gemini-1.5-flash | gpt-4o-mini |
| Cost | Free tier: 15 req/min, 1M tokens/day | $0.15/1M input, $0.60/1M output |
| Speed | Fast (~1-2s response) | Fast (~1-2s response) |
| Quality | High quality, suitable for education | High quality, proven reliability |
| Use Case | Default for cost savings | Fallback if rate limits hit |

### Alternatives Considered
1. **OpenAI Only**: Rejected due to higher costs and no free tier
2. **Gemini Only (No SDK)**: Rejected due to constitution mandate for OpenAI Agents SDK
3. **Custom Agent Framework**: Rejected as over-engineering; OpenAI SDK is battle-tested

### References
- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [OpenAI Agent Custom Models](https://platform.openai.com/docs/agents/custom-models)
- [Google Generative AI SDK](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
- [Gemini Chat Completion Interface](https://ai.google.dev/gemini-api/docs/text-generation)

---

## 2. Model Selection (Dual API Configuration)

### Decision
Use Gemini gemini-1.5-flash as primary model and OpenAI gpt-4o-mini as secondary, both configured within OpenAI Agents SDK framework. Use corresponding embedding models: Gemini text-embedding-004 (primary) and OpenAI text-embedding-3-small (secondary).

### Rationale
- **Cost Efficiency**: Gemini offers generous free tier (15 req/min, 1M tokens/day for gemini-1.5-flash)
- **SDK Compatibility**: OpenAI Agents SDK supports custom models through chat completion interface
- **Performance**: Both models provide fast response times suitable for chat (~1-2s)
- **Flexibility**: Can switch between providers via LLM_PROVIDER environment variable
- **Constitution Compliance**: Using SDK as mandated while optimizing for cost

### Implementation Pattern
```python
# config.py
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # Default to Gemini for cost savings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configurations
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_EMBEDDING_MODEL = "text-embedding-004"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

# agent_service.py
from openai_agents import Agent
import google.generativeai as genai

class AgentService:
    def __init__(self):
        if LLM_PROVIDER == "gemini":
            # Configure Gemini through SDK
            model_config = {
                "model": GEMINI_MODEL,
                "api_key": GEMINI_API_KEY,
                "base_url": "https://generativelanguage.googleapis.com/v1beta"
            }
        else:
            # Configure OpenAI
            model_config = {
                "model": OPENAI_MODEL,
                "api_key": OPENAI_API_KEY
            }

        self.agent = Agent(
            **model_config,
            tools=[vector_search_tool, retrieve_context_tool],
            system_prompt="""You are a helpful teaching assistant..."""
        )

# embedding_service.py
class EmbeddingService:
    async def generate_embedding(self, text: str) -> list[float]:
        if LLM_PROVIDER == "gemini":
            # Use Gemini embeddings
            result = genai.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                content=text
            )
            return result['embedding']  # 768-dim vector
        else:
            # Use OpenAI embeddings
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = await client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding  # 768-dim vector
```

### Cost Comparison

| Provider | Model | Cost | Free Tier | Use Case |
|----------|-------|------|-----------|----------|
| **Gemini (Primary)** | gemini-1.5-flash | Free tier: 15 req/min, 1M tokens/day | Yes | Default for cost savings |
| **OpenAI (Secondary)** | gpt-4o-mini | $0.15/1M input, $0.60/1M output | No | Fallback if rate limits hit |
| **Gemini Embeddings** | text-embedding-004 | Free tier | Yes | Default for cost savings |
| **OpenAI Embeddings** | text-embedding-3-small | $0.02/1M tokens | No | Fallback option |

### Switching Logic
```python
# Switch via environment variable
LLM_PROVIDER=gemini  # Use Gemini (default)
LLM_PROVIDER=openai  # Use OpenAI

# Or switch programmatically if rate limit hit
if gemini_rate_limit_exceeded:
    LLM_PROVIDER = "openai"
```

### Alternatives Considered
1. **OpenAI Only**: Rejected due to higher costs and no free tier
2. **Gemini Only (No SDK)**: Rejected due to constitution mandate for OpenAI Agents SDK
3. **Multiple Providers (Gemini, OpenAI, Claude)**: Rejected as over-engineering for MVP

### References
- [OpenAI Agents SDK Custom Models](https://platform.openai.com/docs/agents/custom-models)
- [Google Generative AI Python SDK](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [OpenAI Models Pricing](https://openai.com/api/pricing/)
- [Gemini Embeddings Guide](https://ai.google.dev/gemini-api/docs/embeddings)

---

## 2. Model Selection (OpenAI)

### Decision
Use OpenAI gpt-4o-mini as the primary model within the OpenAI Agents SDK framework, with OpenAI text-embedding-3-small for embeddings.

### Rationale
- **SDK Compatibility**: OpenAI Agents SDK is designed for OpenAI models
- **Cost Efficiency**: gpt-4o-mini is cost-effective ($0.15/1M input tokens, $0.60/1M output tokens)
- **Performance**: Fast response times suitable for chat (comparable to gemini-1.5-flash)
- **Embeddings**: text-embedding-3-small provides 768-dim vectors at $0.02/1M tokens
- **Constitution Compliance**: Using SDK as mandated takes precedence over specific model preference

### Implementation Pattern
```python
# config.py
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

# agent_service.py
agent = Agent(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    tools=[vector_search_tool, retrieve_context_tool]
)

# embedding_service.py
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_embedding(text: str) -> list[float]:
    response = await client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding  # 768-dim vector
```

### Alternatives Considered
1. **Gemini API**: Rejected because OpenAI Agents SDK doesn't support Gemini models
2. **gpt-4o**: Rejected due to higher cost; gpt-4o-mini sufficient for educational chatbot
3. **Custom Model Adapter**: Rejected as over-engineering; stick with SDK-native models

### References
- [OpenAI Models Pricing](https://openai.com/api/pricing/)
- [gpt-4o-mini Documentation](https://platform.openai.com/docs/models/gpt-4o-mini)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## 3. Vector Database Setup (Qdrant)

### Decision
Use Qdrant Cloud Free Tier with 768-dimensional embeddings (Gemini text-embedding-004 primary, OpenAI text-embedding-3-small secondary), storing textbook chunks with metadata (chapter, section, page, URL).

### Rationale
- **Free Tier**: 1GB storage, 100k vectors - sufficient for 17 textbook chapters (~1,000-2,000 chunks)
- **Performance**: Sub-500ms search latency for top-k retrieval
- **Metadata Filtering**: Supports filtering by chapter/section for source attribution
- **Python SDK**: Well-documented async client for FastAPI integration
- **Managed Service**: No infrastructure management required
- **Confidence Calculation**: Qdrant returns cosine similarity scores in 0.0-1.0 range, directly usable for 0.7 threshold
- **Embedding Flexibility**: Works with both Gemini and OpenAI embeddings (both 768-dim)

### Implementation Pattern
```python
# Vector collection schema
collection_config = {
    "vectors": {
        "size": 768,  # Both Gemini text-embedding-004 and OpenAI text-embedding-3-small use 768-dim
        "distance": "Cosine"
    }
}

# Chunk metadata structure
metadata = {
    "chapter_name": "Module 3: NVIDIA Isaac",
    "section_number": "3.2",
    "page_number": 45,
    "url": "/docs/module-3-isaac/isaac-sim#section-3-2",
    "content_type": "explanation"  # or "code", "diagram_caption"
}

# Search with confidence threshold (cosine similarity 0.0-1.0)
results = await qdrant_client.search(
    collection_name="textbook_chunks",
    query_vector=question_embedding,  # From Gemini or OpenAI embedding service
    limit=5,
    score_threshold=0.7  # Constitution requirement: cosine similarity >= 0.7
)
```

### Chunking Strategy
- **Chunk Size**: 500-1000 tokens per chunk (balance between context and precision)
- **Overlap**: 100 tokens overlap between chunks to preserve context
- **Splitting**: Split on paragraph boundaries, preserve code blocks intact
- **Metadata**: Store chapter/section/URL with each chunk for source attribution
- **Validation**: Verify 768-dim embeddings, metadata schema, test retrieval with "What is VSLAM?"

### Alternatives Considered
1. **Pinecone**: Rejected due to limited free tier (1 index, 100k vectors but requires credit card)
2. **Weaviate**: Rejected due to more complex setup and less generous free tier
3. **ChromaDB**: Rejected as it's designed for local/embedded use, not cloud-managed
4. **PostgreSQL pgvector**: Rejected due to complexity of managing vector indexes and lower performance

### References
- [Qdrant Python Client Documentation](https://qdrant.tech/documentation/quick-start/)
- [Qdrant Cloud Free Tier](https://qdrant.tech/pricing/)
- [Gemini Embeddings API](https://ai.google.dev/gemini-api/docs/embeddings)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## 4. RAG Architecture Pattern (SDK-Driven)

### Decision
Implement RAG as an agent-orchestrated workflow where the OpenAI Agents SDK manages tool calling and response generation, rather than a direct three-stage pipeline.

### Rationale
- **Constitution Compliance**: SDK-based approach satisfies Principle V mandate
- **Agentic Orchestration**: Agent decides when to call tools based on conversation context
- **Flexibility**: Agent can skip vector search for selection mode or follow-up questions
- **Error Handling**: SDK handles tool failures and retries automatically
- **Conversation Memory**: SDK maintains conversation history across turns

### Architecture Flow
```
User Question
    ↓
Agent Service (OpenAI Agents SDK)
    ↓
Agent analyzes question
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

### Tool Implementations

**vector_search_tool.py**:
```python
@tool
async def vector_search_tool(question: str) -> dict:
    """Search Qdrant for relevant textbook chunks."""
    embedding = await embedding_service.generate_embedding(question)
    results = await vector_service.search(
        embedding=embedding,
        limit=5,
        threshold=0.7  # Cosine similarity threshold
    )
    return {
        "chunks": results,
        "confidence": max([r.score for r in results]) if results else 0.0
    }
```

**retrieve_context_tool.py**:
```python
@tool
async def retrieve_context_tool(chunks: list) -> dict:
    """Format retrieved chunks with source metadata."""
    context = "\n\n".join([c.content for c in chunks])
    sources = [
        {
            "chapter": c.metadata["chapter_name"],
            "section": c.metadata["section_number"],
            "url": c.metadata["url"]
        }
        for c in chunks
    ]
    return {"context": context, "sources": sources}
```

### Selection Mode Handling
When `selected_text` is provided:
- Agent skips calling `vector_search_tool`
- Uses `selected_text` directly as context
- Still includes source attribution from metadata

### Uncertainty Handling
System prompt instructs agent:
- "Only answer using provided context"
- "If context insufficient, state 'I don't have information about this in the textbook'"
- "Suggest related topics that ARE covered"

### Alternatives Considered
1. **Direct Pipeline (Embed → Retrieve → Generate)**: Rejected due to SDK mandate
2. **LangChain RAG**: Rejected as constitution requires OpenAI Agents SDK specifically
3. **Custom Tool Orchestration**: Rejected; SDK handles this better

### References
- [OpenAI RAG Agents Pattern](https://platform.openai.com/docs/guides/rag-agents)
- [Agent Tool Best Practices](https://platform.openai.com/docs/agents/tools/best-practices)

---

## 5. Docusaurus Integration Strategy

### Decision
Integrate chat UI as custom Docusaurus theme components: (1) Wrap app in Root.tsx with ChatProvider, (2) Add floating ChatButton component, (3) Render ChatPanel as slide-out overlay.

### Rationale
- **Theme Integration**: Docusaurus theme system allows custom React components without ejecting
- **State Management**: React Context API for chat state (messages, conversations, UI state)
- **Theme Matching**: Access Docusaurus design tokens via CSS variables for consistent styling
- **Non-Invasive**: Doesn't modify existing textbook pages, only adds overlay UI

### Implementation Pattern
```typescript
// src/theme/Root.tsx
import { ChatProvider } from '../contexts/ChatContext';
import ChatButton from '../components/ChatButton';
import ChatPanel from '../components/ChatPanel';

export default function Root({ children }) {
  return (
    <ChatProvider>
      {children}
      <ChatButton />
      <ChatPanel />
    </ChatProvider>
  );
}

// CSS theme matching
.chatPanel {
  background: var(--ifm-background-color);
  color: var(--ifm-font-color-base);
  border: 1px solid var(--ifm-color-emphasis-300);
}
```

### Text Selection Detection
```typescript
// useTextSelection.ts
export function useTextSelection() {
  const [selectedText, setSelectedText] = useState('');

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      setSelectedText(selection?.toString() || '');
    };

    document.addEventListener('selectionchange', handleSelection);
    return () => document.removeEventListener('selectionchange', handleSelection);
  }, []);

  return selectedText;
}
```

### Alternatives Considered
1. **Docusaurus Plugin**: Rejected as plugins are for build-time features, not runtime UI
2. **Separate Chat Page**: Rejected as it breaks user flow (students must leave textbook)
3. **Iframe Embed**: Rejected due to styling challenges and cross-origin issues
4. **Browser Extension**: Rejected as it requires users to install extension (poor UX)

### References
- [Docusaurus Swizzling Guide](https://docusaurus.io/docs/swizzling)
- [Docusaurus Theming](https://docusaurus.io/docs/styling-layout)
- [React Context API](https://react.dev/reference/react/useContext)

---

## 6. Conversation Management

### Decision
Store conversations in Neon Postgres with 12-month retention policy, auto-generate titles from first 50 characters of first question, display conversation list in sidebar.

### Rationale
- **Persistence**: Postgres ensures reliable storage across sessions
- **Retention**: 12-month policy (per clarification) balances student needs with storage costs
- **Title Generation**: Simple truncation avoids AI processing overhead
- **Sidebar Navigation**: Standard chat UX pattern (Slack, Discord, ChatGPT)

### Database Schema
```sql
-- conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(100) NOT NULL,  -- First 50 chars + "..."
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    message_count INTEGER NOT NULL DEFAULT 0,
    last_message_at TIMESTAMP
);

-- chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'ai')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    source_references JSONB  -- Array of {chapter, section, url}
);

-- Indexes
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
CREATE INDEX idx_messages_conversation ON chat_messages(conversation_id, created_at);

-- Retention policy (run daily)
DELETE FROM conversations
WHERE last_message_at < NOW() - INTERVAL '12 months';
```

### Alternatives Considered
1. **AI-Generated Titles**: Rejected due to added latency and API costs
2. **Timestamp-Only Titles**: Rejected as less user-friendly (hard to identify conversations)
3. **Redis for Chat History**: Rejected as Postgres provides better durability and querying
4. **Indefinite Retention**: Rejected due to storage costs and privacy concerns

### References
- [Neon Postgres Documentation](https://neon.tech/docs/introduction)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [FastAPI with asyncpg](https://fastapi.tiangolo.com/advanced/async-sql-databases/)

---

## 7. Testing Strategy

### Decision
Implement TDD with three test layers: (1) Unit tests for services (pytest), (2) Integration tests for API endpoints (TestClient), (3) E2E tests for chat flow (Playwright).

### Rationale
- **Constitution Compliance**: Satisfies Principle II (TDD, 80% coverage)
- **Fast Feedback**: Unit tests run in <1 second, catch logic errors early
- **API Validation**: Integration tests verify endpoint contracts
- **User Flow**: E2E tests validate complete chat experience

### Test Structure
```python
# Unit test example (test_agent_service.py)
@pytest.mark.asyncio
async def test_agent_orchestrates_rag_flow():
    # Arrange
    mock_vector_tool = Mock()
    mock_vector_tool.execute.return_value = {
        "chunks": [{"score": 0.85, "content": "VSLAM stands for..."}],
        "confidence": 0.85
    }
    agent_service = AgentService(tools=[mock_vector_tool])

    # Act
    response = await agent_service.process_question("What is VSLAM?")

    # Assert
    assert response["confidence"] >= 0.7
    assert "VSLAM" in response["answer"]
    assert len(response["sources"]) > 0

# Integration test example (test_chat_api.py)
def test_send_message_authenticated(client, auth_token):
    response = client.post(
        "/api/v1/chat/messages",
        json={"conversation_id": "...", "content": "What is VSLAM?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "sources" in response.json()

# E2E test example (chat-flow.spec.ts)
test('student can ask question and receive answer', async ({ page }) => {
    await page.goto('/docs/module-3-isaac/isaac-sim');
    await page.click('[data-testid="chat-button"]');
    await page.fill('[data-testid="message-input"]', 'What is VSLAM?');
    await page.click('[data-testid="send-button"]');
    await expect(page.locator('[data-testid="ai-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="source-link"]')).toBeVisible();
});
```

### Coverage Targets
- Unit tests: 85% coverage (agent service, tools, utilities)
- Integration tests: 90% coverage (API endpoints)
- E2E tests: Critical user flows (ask question, view history, switch conversations)
- Accessibility tests: Keyboard navigation, screen readers, WCAG 2.1 AA

**Unit Tests** (80% coverage minimum):
- Agent service: Test agent initialization, tool registration, orchestration flow
- Vector service: Test Qdrant search, threshold filtering, cosine similarity validation
- Embedding service: Test OpenAI embedding generation (768-dim)
- Chat service: Test conversation creation, message persistence, title generation edge cases
- Agent tools: Test vector_search_tool and retrieve_context_tool independently

**Integration Tests**:
- Chat API: Test full request/response cycle with authentication
- Agent + Tools: Test agent calling tools correctly
- Database: Test conversation and message persistence

**E2E Tests** (Playwright):
- User flow: Login → Ask question → Verify response with sources
- Selection mode: Select text → Ask question → Verify focused response
- Error handling: Test unauthenticated access, expired session, network errors
- Accessibility: Keyboard navigation, screen readers, WCAG 2.1 AA compliance

### Alternatives Considered
1. **Manual Testing Only**: Rejected due to constitution requirement for TDD
2. **Integration Tests Only**: Rejected as unit tests provide faster feedback
3. **Selenium for E2E**: Rejected in favor of Playwright (better async support, faster)

### References
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Playwright for Python](https://playwright.dev/python/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Primary LLM | Google Gemini (gemini-1.5-flash) | Cost-effective, fast, generous free tier |
| Secondary LLM | OpenAI (gpt-4o-mini) | Fallback option, constitution requirement |
| Vector DB | Qdrant Cloud Free Tier | 1GB storage, 100k vectors, managed service |
| Embeddings | Google text-embedding-004 (768-dim) | Matches Gemini ecosystem, high quality |
| RAG Pattern | Retrieve (k=5, threshold=0.7) → Generate | Simple, effective, constitution-compliant |
| UI Integration | Docusaurus theme components (Root.tsx) | Non-invasive, theme-matched, standard React |
| Conversation Storage | Neon Postgres with 12-month retention | Reliable, queryable, cost-effective |
| Testing | TDD with 3 layers (unit, integration, E2E) | Constitution-compliant, comprehensive coverage |

---

## Open Questions Resolved

All technical unknowns from Technical Context have been resolved through research:
- ✅ Gemini API integration pattern documented
- ✅ Qdrant vector search strategy defined
- ✅ RAG pipeline architecture specified
- ✅ Docusaurus theming approach clarified
- ✅ Conversation management schema designed
- ✅ Testing strategy established

**Ready to proceed to Phase 1: Design & Contracts**
