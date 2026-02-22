---
id: 004
title: Add RAG Chatbot Architecture Principles
stage: constitution
date: 2026-02-22
surface: agent
model: claude-opus-4-6
feature: none
branch: 003-rag-chatbot
user: ahmeddev
command: /sp.constitution
labels: ["constitution", "rag-chatbot", "gemini-api", "openai-api", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (constitution amendment)
---

## Prompt

update the constitutiton  about rag chatbot implementation
The chatbot must prioritize information found in the textbook over its general knowledge to ensure students receive course-specific answers

All backend logic must use FastAPI, with Neon Serverless Postgres for structured data and Qdrant Cloud for vector storage.

Mandatory Frameworks: The chatbot backend must be built using FastAPI.

Vector Database: Qdrant Cloud (Free Tier) must be used for storing and retrieving document embeddings.

Relational Database: Neon Serverless Postgres is required for storing structured data such as chat history or user sessions.

Agentic Core: The chatbot must utilize the OpenAI Agent SDK to manage its logic and capabilities(for chatbot).

Docusaurus Integration: The chatbot UI must be natively embedded as a component within the Docusaurus book structure.

Strict RAG Grounding: The chatbot must prioritize information found within the uploaded textbook chapters over its general training data.

Source Attribution: Responses should include references or links to the specific chapter or section of the book from which the information was retrieved.

Selection Sensitivity: The system must implement a specialized mode to answer questions based only on text currently selected by the user in the browser.

Handle Uncertainty: If a question cannot be answered using the book's content, the bot must clearly state its limitations rather than hallucinating facts about robotics.

The bot should maintain a professional, academic, yet encouraging tone suitable for a technical textbook

The bot should simplify complex Physical AI concepts (like VSLAM or Bipedal Locomotion) into step-by-step explanations for students.

refine these constitution by your self

ADDITIONAL REQUIREMENT: before moving forward i also add one more thing alwayd do two setup for api on eis for gemini api key thorugh chst complition model or any other which is suitable and one is for open ai , comment out the open ai and use the gemini api key configurations

## Response snapshot

Constitution updated from v1.2.0 to v2.0.0 (MAJOR version bump).

**Added Principle X: RAG Chatbot Architecture** with 5 mandatory subsections:

A. **Strict RAG Grounding (MANDATORY)**
   - Retrieve from Qdrant before generating responses
   - Confidence threshold: 0.7 minimum
   - Explicit limitation statements when no relevant content found

B. **Source Attribution (MANDATORY)**
   - Include clickable links to source chapters
   - Display multiple sources if answer draws from multiple sections
   - Format: "Source: [Chapter Name](URL) - Section X.Y"

C. **Selection-Based Context (REQUIRED)**
   - Support "Ask about selection" mode
   - Use selected text as primary context (skip Qdrant retrieval)
   - Fall back to full RAG if no text selected

D. **Uncertainty Handling (MANDATORY)**
   - Never hallucinate facts about Physical AI or robotics
   - Use explicit phrases: "I don't have information about this in the textbook"
   - Suggest related topics that ARE covered
   - Prohibited: Making up ROS 2 commands, NVIDIA Isaac features, hardware specs

E. **Tone and Pedagogy (REQUIRED)**
   - Professional, academic, encouraging tone
   - Break down complex concepts (VSLAM, Bipedal Locomotion) into steps
   - Use analogies when helpful
   - Acknowledge advanced topics and suggest prerequisites

**Added Dual API Configuration (MANDATORY)**:
- **Primary (Active)**: Google Gemini API (gemini-1.5-flash or gemini-1.5-pro)
  - Active by default in code
  - Cost-effective with generous free tier
- **Secondary (Commented)**: OpenAI API (gpt-4o-mini or gpt-4o)
  - Commented out but ready to activate
  - Same interface/abstraction as Gemini
- **Switching**: Developers can switch by commenting/uncommenting config lines and changing environment variables

**Tech Stack Requirements Updated**:
- FastAPI (Python 3.11+) with async/await
- Neon Serverless Postgres (structured data, chat history)
- Qdrant Cloud Free Tier (vector embeddings, 768-dim)
- Gemini API (primary) + OpenAI API (secondary)
- Better-Auth (JWT authentication)
- Docusaurus 3.x (chatbot UI embedded as theme component)

## Outcome

- ✅ Impact: Constitution v2.0.0 ratified with comprehensive RAG chatbot architecture principles
- 🧪 Tests: None (constitution document)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify (create Phase 3 RAG chatbot specification)
- 🧠 Reflection: Major version bump justified by adding mandatory architectural constraints that affect all future chatbot development. Dual API configuration ensures cost flexibility and vendor independence.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution amendment)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create Phase 3 specification following new RAG principles
