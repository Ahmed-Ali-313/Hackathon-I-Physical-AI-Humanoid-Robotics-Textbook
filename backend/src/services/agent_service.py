"""
Agent service using OpenAI Agents SDK for RAG orchestration.

Manages agent initialization, tool registration, and conversation flow.
Uses OpenAI gpt-4o-mini model for chat responses.
"""

from typing import List, Dict, Any, Optional
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class AgentService:
    """
    Service for managing OpenAI Agents SDK agent.

    Handles agent initialization with OpenAI models, tool registration,
    and RAG orchestration for textbook Q&A.
    """

    def __init__(self):
        """
        Initialize agent service with OpenAI.

        Raises:
            ValueError: If OPENAI_API_KEY is not configured
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # Agent configuration
        self.model_name = "gpt-4o-mini"
        self.agent = None
        self.tools = []

        # System prompt for tone and pedagogy (FR-027 to FR-030)
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """
        Build system prompt for agent with tone and pedagogy guidelines.

        Implements FR-027 to FR-030:
        - FR-027: Professional, academic tone
        - FR-028: Step-by-step explanations
        - FR-029: Use analogies for complex concepts
        - FR-030: Suggest prerequisites when needed

        Returns:
            System prompt string
        """
        return """You are an AI teaching assistant for a Physical AI & Humanoid Robotics textbook.

**Your Role:**
- Answer student questions using ONLY the provided textbook content
- Help students understand complex robotics concepts
- Guide students through learning progressions

**Tone & Style (FR-027):**
- Use professional, academic language
- Be clear, precise, and technically accurate
- Maintain a supportive, encouraging tone
- Avoid casual language or slang

**Explanation Approach (FR-028):**
- Break down complex concepts into step-by-step explanations
- Start with fundamentals before advanced details
- Use numbered lists for multi-step processes
- Provide concrete examples when possible

**Teaching Techniques (FR-029):**
- Use analogies to explain abstract concepts
- Relate new concepts to familiar ideas
- Compare and contrast related concepts
- Use real-world examples from robotics applications

**Learning Guidance (FR-030):**
- When students ask advanced questions, check if they understand prerequisites
- Suggest foundational topics to study first when needed
- Recommend related chapters for deeper understanding
- Acknowledge when a topic requires background knowledge

**Strict RAG Grounding:**
- ONLY answer using the provided textbook context
- If the context is insufficient, state: "I don't have information about this in the textbook"
- When uncertain, suggest related topics that ARE covered in the textbook
- Never make up information or use knowledge outside the textbook

**Source Attribution:**
- Always cite the textbook chapter/section for your answers
- Provide clickable links to relevant sections
- Include 1-5 source references per response

**Response Format:**
1. Direct answer to the question
2. Step-by-step explanation (if applicable)
3. Analogies or examples (if helpful)
4. Prerequisites or related topics (if needed)
5. Source references with links

Remember: Your goal is to help students learn effectively by providing accurate, well-explained answers grounded in the textbook content."""

    def register_tool(self, tool: Any):
        """
        Register a tool with the agent.

        Args:
            tool: Tool instance to register
        """
        self.tools.append(tool)

    def register_tools(self, tools: List[Any]):
        """
        Register multiple tools with the agent.

        Args:
            tools: List of tool instances to register
        """
        self.tools.extend(tools)

    async def initialize_agent(self):
        """
        Initialize the OpenAI Agents SDK agent.

        Creates agent with configured model, system prompt, and registered tools.

        Raises:
            Exception: If agent initialization fails
        """
        try:
            # TODO: Implement OpenAI Agents SDK initialization
            # This will be implemented when the SDK is available
            # For now, this is a placeholder structure

            # Example structure (to be implemented):
            # from openai_agents import Agent
            # self.agent = Agent(
            #     model=self.model_name,
            #     system_prompt=self.system_prompt,
            #     tools=self.tools,
            #     api_key=self._get_api_key(),
            # )

            pass

        except Exception as e:
            raise Exception(f"Failed to initialize agent: {e}")

    def _get_api_key(self) -> str:
        """
        Get OpenAI API key.

        Returns:
            API key string
        """
        return settings.openai_api_key

    async def generate_response(
        self,
        question: str,
        selected_text: Optional[str] = None,
        selected_text_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate response to user question using RAG.

        Implements RAG orchestration:
        1. Selection mode: Use selected_text as context (skip vector search)
        2. Normal mode: Search Qdrant → Retrieve context → Generate response
        3. Uncertainty handling: Return "I don't have information" if no context

        Args:
            question: User's question
            selected_text: Optional selected text for context
            selected_text_metadata: Optional metadata for selected text

        Returns:
            Response dictionary with content, confidence, and sources

        Raises:
            ValueError: If question is empty
            Exception: If response generation fails
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        try:
            # Get tools from registry
            vector_search_tool = self._get_tool("vector_search")
            retrieve_context_tool = self._get_tool("retrieve_context")

            # Selection mode: Use selected text as context (FR-014, FR-015)
            if selected_text and selected_text.strip():
                return await self._generate_response_with_selection(
                    question=question,
                    selected_text=selected_text,
                    selected_text_metadata=selected_text_metadata,
                    retrieve_context_tool=retrieve_context_tool,
                )

            # Normal mode: RAG with vector search
            return await self._generate_response_with_rag(
                question=question,
                vector_search_tool=vector_search_tool,
                retrieve_context_tool=retrieve_context_tool,
            )

        except ConnectionError as e:
            logger.error(f"Qdrant connection error: {str(e)}")
            raise ConnectionError("Unable to connect to the search service. Please check your connection and try again.")

        except TimeoutError as e:
            logger.error(f"Request timeout: {str(e)}")
            raise TimeoutError("The request took too long to complete. Please try again.")

        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            raise ValueError(f"Invalid input: {str(e)}")

        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}", exc_info=True)
            raise Exception(f"An unexpected error occurred while generating response: {str(e)}")

    async def _generate_response_with_selection(
        self,
        question: str,
        selected_text: str,
        selected_text_metadata: Optional[Dict[str, Any]],
        retrieve_context_tool: Any,
    ) -> Dict[str, Any]:
        """
        Generate response using selected text as context (selection mode).

        Args:
            question: User's question
            selected_text: Selected text from textbook
            selected_text_metadata: Metadata for selected text
            retrieve_context_tool: Tool for formatting context

        Returns:
            Response dictionary
        """
        # Format selected text as context
        metadata = selected_text_metadata or {}
        mock_search_result = [{
            "content": selected_text,
            "confidence": 1.0,  # Selected text has full confidence
            "metadata": {
                "chapter": metadata.get("chapter", "selected"),
                "module": metadata.get("module", "selected"),
                "section": metadata.get("section", "selected"),
                "url": metadata.get("url", ""),
            }
        }]

        context_data = await retrieve_context_tool.execute(mock_search_result)
        sources = retrieve_context_tool.format_sources_for_response(context_data["sources"])

        # Generate response using selected text as context
        # TODO: Replace with actual LLM call when SDK is integrated
        response_content = self._generate_mock_response(question, context_data["context"], is_selection=True)

        return {
            "content": response_content,
            "confidence_score": 1.0,
            "source_references": sources,
        }

    async def _generate_response_with_rag(
        self,
        question: str,
        vector_search_tool: Any,
        retrieve_context_tool: Any,
    ) -> Dict[str, Any]:
        """
        Generate response using RAG (vector search + context retrieval).

        Args:
            question: User's question
            vector_search_tool: Tool for searching Qdrant
            retrieve_context_tool: Tool for formatting context

        Returns:
            Response dictionary
        """
        # Step 1: Search Qdrant for relevant chunks (uses config threshold, top-5)
        search_results = await vector_search_tool.execute(
            query=question,
            top_k=5,
        )

        # Step 2: Retrieve and format context
        context_data = await retrieve_context_tool.execute(search_results)

        # Step 3: Check if context is sufficient (FR-017, FR-018)
        if not context_data["has_context"]:
            return self._generate_uncertainty_response(question)

        # Step 4: Calculate average confidence score
        avg_confidence = self._calculate_average_confidence(context_data["sources"])

        # Step 5: Format sources for response
        sources = retrieve_context_tool.format_sources_for_response(context_data["sources"])

        # Step 6: Generate response using context
        # TODO: Replace with actual LLM call when SDK is integrated
        response_content = self._generate_mock_response(question, context_data["context"], is_selection=False)

        return {
            "content": response_content,
            "confidence_score": avg_confidence,
            "source_references": sources,
        }

    def _generate_uncertainty_response(self, question: str) -> Dict[str, Any]:
        """
        Generate uncertainty response when no context is found (FR-017, FR-018).

        Args:
            question: User's question

        Returns:
            Response dictionary with uncertainty message
        """
        # Hallucination prevention (T026a): Explicit uncertainty handling
        response_content = (
            "I don't have information about this in the textbook. "
            "This topic may not be covered in the current chapters, or it might be discussed "
            "under a different name.\n\n"
            "**Suggested related topics:**\n"
            "- ROS 2 Middleware and Communication\n"
            "- Digital Twin Simulation (Gazebo, Unity)\n"
            "- NVIDIA Isaac Sim and Isaac ROS\n"
            "- Vision-Language-Action (VLA) Models\n\n"
            "Try rephrasing your question or exploring these related topics in the textbook."
        )

        return {
            "content": response_content,
            "confidence_score": 0.0,
            "source_references": [],
        }

    def _calculate_average_confidence(self, sources: List[Dict[str, Any]]) -> float:
        """
        Calculate average confidence score from sources.

        Args:
            sources: List of source dictionaries with confidence scores

        Returns:
            Average confidence score (0.0-1.0)
        """
        if not sources:
            return 0.0

        total_confidence = sum(source.get("confidence", 0.0) for source in sources)
        return round(total_confidence / len(sources), 2)

    def _generate_mock_response(self, question: str, context: str, is_selection: bool) -> str:
        """
        Generate mock response (placeholder until LLM integration).

        Args:
            question: User's question
            context: Retrieved context
            is_selection: Whether this is selection mode

        Returns:
            Mock response string
        """
        # TODO: Replace with actual LLM call using OpenAI Agents SDK
        # This is a placeholder that will be replaced with:
        # response = await self.agent.generate(
        #     prompt=question,
        #     context=context,
        #     system_prompt=self.system_prompt,
        # )

        if is_selection:
            return f"Based on the selected text, here's an explanation: {context[:200]}..."
        else:
            return f"Based on the textbook content: {context[:200]}..."

    def _get_tool(self, tool_name: str) -> Any:
        """
        Get a tool by name from registered tools.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance

        Raises:
            ValueError: If tool not found
        """
        for tool in self.tools:
            if hasattr(tool, 'name') and tool.name == tool_name:
                return tool

        raise ValueError(f"Tool '{tool_name}' not found. Make sure tools are registered.")

    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the current model configuration.

        Returns:
            Dictionary with provider and model name
        """
        return {
            "provider": "openai",
            "model": self.model_name,
        }


# Global agent service instance
agent_service = AgentService()
