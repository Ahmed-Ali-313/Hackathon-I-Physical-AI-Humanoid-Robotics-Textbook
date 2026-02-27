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

**Your Identity:**
- You are a helpful teaching assistant specializing in Physical AI and Humanoid Robotics
- You can greet students, introduce yourself, and have brief conversational exchanges
- For greetings like "hello" or "hi", respond warmly and offer to help with textbook questions
- For identity questions like "who are you", explain you're a teaching assistant for this robotics textbook

**Your Role:**
- Answer technical questions using ONLY the provided textbook content
- Help students understand complex robotics concepts
- Guide students through learning progressions
- ALWAYS follow user instructions (e.g., "explain simply", "in detail", "step by step")

**CRITICAL: Response Structure and Formatting**
Your responses MUST be well-structured and easy to read:

1. **Use Clear Markdown Formatting:**
   - Use ## for main headings (e.g., ## What is ROS 2?)
   - Use ### for subheadings (e.g., ### Key Features)
   - Use **bold** for important terms
   - Use numbered lists (1., 2., 3.) for sequential steps
   - Use bullet points (-, *, •) for feature lists
   - **MANDATORY: Use double line breaks (\n\n) between ALL paragraphs and headings**
   - **MANDATORY: Add blank lines before and after every heading**
   - **MANDATORY: Add blank lines before and after every list**

2. **Organize Content Hierarchically:**
   - Start with a brief direct answer (1-2 sentences)
   - Then provide detailed explanation with clear sections
   - Use headings to separate different aspects
   - End with references/sources
   - **CRITICAL: Never create "wall of text" - always separate paragraphs with \n\n**

3. **Example Structure (FOLLOW THIS EXACTLY):**
   ```
   ## Topic Name

   [Brief 1-2 sentence direct answer]

   ### Main Concept

   [Explanation paragraph with proper spacing]

   [Another paragraph if needed - always separated by blank line]

   ### Key Features

   1. First feature - explanation
   2. Second feature - explanation
   3. Third feature - explanation

   ### How It Works

   - Step 1: Description
   - Step 2: Description
   - Step 3: Description

   ### Example

   [Code or practical example if relevant]

   ### References

   - [Source 1](#)
   - [Source 2](#)
   ```

**SPACING RULES (CRITICAL):**
- Always add \n\n after headings (##, ###)
- Always add \n\n between paragraphs
- Always add \n\n before and after lists
- Never put text immediately after a heading without a blank line
- This ensures professional, scannable responses

**Tone & Style (FR-027):**
- Use professional, academic language for technical content
- Be clear, precise, and technically accurate
- Maintain a supportive, encouraging tone
- Adapt complexity based on user's request (simple vs detailed)

**CRITICAL: Follow User Instructions:**
- If user says "explain in very simple way" → Use simple language, short sentences, everyday analogies
- If user says "explain in detail" → Provide comprehensive, technical explanation
- If user says "step by step" → Use numbered steps
- ALWAYS adapt your response style to match what the user asks for

**Explanation Approach (FR-028):**
- Break down complex concepts into step-by-step explanations
- Start with fundamentals before advanced details
- Use numbered lists for multi-step processes
- Provide concrete examples when possible
- When asked to simplify, use everyday language and avoid jargon

**Teaching Techniques (FR-029):**
- Use analogies to explain abstract concepts (especially when asked to simplify)
- Relate new concepts to familiar ideas
- Compare and contrast related concepts
- Use real-world examples from robotics applications

**Learning Guidance (FR-030):**
- When students ask advanced questions, check if they understand prerequisites
- Suggest foundational topics to study first when needed
- Recommend related chapters for deeper understanding
- Acknowledge when a topic requires background knowledge

**Strict RAG Grounding (ONLY for technical questions):**
- For technical/content questions: ONLY answer using the provided textbook context
- If the context is insufficient, state: "I don't have information about this topic in the textbook. However, the textbook covers related topics like [list 2-3 related topics from the textbook]."
- Never make up technical information or use knowledge outside the textbook
- For greetings/identity questions: You can respond naturally without textbook context

**Source Attribution:**
- Always cite the textbook chapter/section for technical answers
- Provide clickable links to relevant sections
- Include 1-5 source references per response
- Format sources as a clean list at the end

**IMPORTANT: Generate COMPLETE responses:**
- Never stop mid-sentence or mid-paragraph
- Ensure your answer fully addresses the question
- If the answer is long, prioritize completeness over brevity
- Finish all thoughts and explanations
- Use proper markdown formatting throughout

Remember: Your goal is to help students learn effectively by providing accurate, well-structured, COMPLETE answers that are easy to read and understand."""

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
        1. Greeting/Identity detection: Handle conversational queries directly
        2. Selection mode: Use selected_text as context (skip vector search)
        3. Normal mode: Search Qdrant → Retrieve context → Generate response
        4. Uncertainty handling: Return "I don't have information" if no context

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

        # Log request
        logger.info(f"Generating response for question: {question[:100]}...")
        logger.debug(f"Selection mode: {bool(selected_text)}")

        try:
            # Check if this is a greeting or identity question (bypass RAG)
            if self._is_conversational_query(question):
                logger.info("Detected conversational query (greeting/identity)")
                return self._generate_conversational_response(question)

            # Get tools from registry
            vector_search_tool = self._get_tool("vector_search")
            retrieve_context_tool = self._get_tool("retrieve_context")

            # Selection mode: Use selected text as context (FR-014, FR-015)
            if selected_text and selected_text.strip():
                logger.info("Using selection mode")
                response = await self._generate_response_with_selection(
                    question=question,
                    selected_text=selected_text,
                    selected_text_metadata=selected_text_metadata,
                    retrieve_context_tool=retrieve_context_tool,
                )
                logger.info(f"Selection mode response generated (confidence: {response['confidence_score']:.2f})")
                return response

            # Normal mode: RAG with vector search
            logger.info("Using RAG mode with vector search")
            response = await self._generate_response_with_rag(
                question=question,
                vector_search_tool=vector_search_tool,
                retrieve_context_tool=retrieve_context_tool,
            )
            logger.info(
                f"RAG response generated (confidence: {response['confidence_score']:.2f}, "
                f"sources: {len(response['source_references'])})"
            )
            return response

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

    def _is_conversational_query(self, question: str) -> bool:
        """
        Check if the question is a greeting or identity query.

        Args:
            question: User's question

        Returns:
            True if conversational query, False otherwise
        """
        question_lower = question.lower().strip()

        # Greeting patterns
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']

        # Identity patterns
        identity_patterns = [
            'who are you', 'what are you', 'who r u', 'what r u',
            'tell me about yourself', 'introduce yourself',
            'what is your name', 'what\'s your name',
            'what do you do', 'what can you do'
        ]

        # Check for exact greetings
        if question_lower in greetings:
            return True

        # Check for identity questions
        for pattern in identity_patterns:
            if pattern in question_lower:
                return True

        return False

    def _generate_conversational_response(self, question: str) -> Dict[str, Any]:
        """
        Generate response for conversational queries (greetings, identity).

        Args:
            question: User's question

        Returns:
            Response dictionary
        """
        question_lower = question.lower().strip()

        # Greeting response
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if question_lower in greetings:
            response_content = (
                "Hello! 👋 I'm your AI teaching assistant for the Physical AI & Humanoid Robotics textbook.\n\n"
                "I'm here to help you understand complex robotics concepts, answer questions about the textbook content, "
                "and guide you through your learning journey.\n\n"
                "**What I can help with:**\n"
                "- Explaining concepts from the textbook\n"
                "- Answering questions about ROS 2, Isaac Sim, Digital Twins, and more\n"
                "- Clarifying selected text passages\n"
                "- Suggesting related topics and prerequisites\n\n"
                "Feel free to ask me any question about the textbook content!"
            )
        else:
            # Identity response
            response_content = (
                "I'm an AI teaching assistant specialized in Physical AI and Humanoid Robotics. "
                "My role is to help students like you understand the textbook content by:\n\n"
                "**My Capabilities:**\n"
                "- Answering questions using the textbook as my knowledge source\n"
                "- Explaining complex concepts in simple terms\n"
                "- Providing step-by-step explanations\n"
                "- Using analogies to make abstract ideas clearer\n"
                "- Suggesting related topics and prerequisites\n"
                "- Citing sources from the textbook chapters\n\n"
                "**Topics I cover:**\n"
                "- ROS 2 Middleware and Communication\n"
                "- Digital Twin Simulation (Gazebo, Unity, Isaac Sim)\n"
                "- NVIDIA Isaac ROS and Isaac Sim\n"
                "- Vision-Language-Action (VLA) Models\n"
                "- Humanoid Robotics and Locomotion\n\n"
                "Ask me anything about these topics from the textbook!"
            )

        return {
            "content": response_content,
            "confidence_score": 1.0,
            "source_references": [],
        }

    def _generate_mock_response(self, question: str, context: str, is_selection: bool) -> str:
        """
        Generate response using OpenAI API.

        Args:
            question: User's question
            context: Retrieved context
            is_selection: Whether this is selection mode

        Returns:
            Generated response string
        """
        import openai

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=self._get_api_key())

        # Build user prompt with context
        if is_selection:
            user_prompt = f"""Question: {question}

Selected Text Context:
{context}

Please answer the question based on the selected text above."""
        else:
            user_prompt = f"""Question: {question}

Textbook Context:
{context}

Please answer the question based on the textbook content above. Provide a COMPLETE answer."""

        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000,  # Allow longer responses
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # Fallback to context preview if API fails
            return f"Based on the textbook content: {context[:500]}..."

    async def _generate_streaming_response(self, question: str, context: str, is_selection: bool):
        """
        Generate streaming response using OpenAI API.

        Args:
            question: User's question
            context: Retrieved context
            is_selection: Whether this is selection mode

        Yields:
            Chunks of the response as they are generated
        """
        import openai

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=self._get_api_key())

        # Build user prompt with context
        if is_selection:
            user_prompt = f"""Question: {question}

Selected Text Context:
{context}

Please answer the question based on the selected text above."""
        else:
            user_prompt = f"""Question: {question}

Textbook Context:
{context}

Please answer the question based on the textbook content above. Provide a COMPLETE answer."""

        try:
            # Call OpenAI API with streaming
            stream = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                stream=True,  # Enable streaming
            )

            # Yield chunks as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming API call failed: {str(e)}")
            # Fallback to non-streaming
            yield f"Based on the textbook content: {context[:500]}..."

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
