
## Agentic-lead-capture-gemini

This project demonstrates a stateful conversational AI agent that converts conversations into qualified leads for a fictional SaaS product, AutoStream.

### Features
- **Intent detection** using Gemini 2.0 Flash
- **RAG with local JSON knowledge base**
- **Stateful multi-turn conversation**
- **Mock lead capture tool** (saves leads to `data/leads.json`)
- **Streamlit-based UI**

### How to Run Locally

**1. Clone or navigate to the project directory:**
```bash
cd autostream-agent-gemini
```

**2. Create a virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Set up your Google API key:**

Create a `.env` file in the project root:
```text
GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

**5. Run the application:**

**Option A: Streamlit UI (Recommended)**
```bash
streamlit run ui.py
```
Then open your browser to `http://localhost:8501`

**Option B: CLI Mode**
```bash
python main.py
```

**Note:** The first run may take a moment to initialize. Make sure you have an active internet connection for API calls.

### Architecture Explanation

This project uses **LangChain** with Gemini 2.0 Flash to implement a stateful, task-focused conversational agent for AutoStream. The agent logic is split into focused modules: `intent.py` for intent classification using Gemini's LLM, `rag.py` for knowledge retrieval from a local JSON knowledge base, `tools.py` for lead capture execution, and `graph.py` as a controller that routes messages based on intent and state.

**Why I chose LangChain:**

LangChain was chosen over LangGraph/AutoGen for three key reasons:

- **Simplicity**: LangChain provides clean abstractions around prompts, LLM calls, and tools without forcing a heavy orchestration layer, making it ideal for straightforward conversational flows.
- **Flexibility**: The modular design allows easy customization of intent detection, RAG retrieval, and tool execution without being locked into a rigid graph structure.
- **Lightweight**: For this use case, a simple state machine is sufficient—we don't need the complex multi-agent orchestration that LangGraph/AutoGen provide.

This modular approach makes the codebase maintainable and allows each component to be tested and modified independently.

**How state is managed:**

State is managed explicitly using a lightweight `AgentState` dataclass that stores the current intent, lead details (name, email, platform), conversation history, and a flag indicating whether the lead has been captured. In the Streamlit UI, this state object persists in `st.session_state`, surviving across multiple turns and supporting multi-step flows like collecting lead information over 5–6 messages. In CLI mode, the state object lives in memory for the session duration. The RAG component uses keyword-based retrieval from a local JSON knowledge base, ensuring answers stay grounded in AutoStream's pricing plans and policies. When high intent is detected and all lead fields are collected, the agent calls `mock_lead_capture` which saves leads to `data/leads.json` for tracking and future reference.

### WhatsApp Deployment (Webhook Integration)

To integrate this agent with WhatsApp using webhooks, deploy a webhook server (FastAPI, Flask, or similar) over HTTPS and configure the WhatsApp Business Cloud API to send incoming messages to the endpoint. When a user sends a message, WhatsApp sends a POST request containing the user's phone number, message text, and metadata.

For each incoming message, extract the WhatsApp user ID and look up or initialize an `AgentState` object for that user, stored in a database (Redis or PostgreSQL) keyed by WhatsApp user ID. This ensures each user has their own conversation state that persists across sessions. Pass the message text and retrieved state to the existing `agent_step()` function—the agent handles intent detection, RAG retrieval, and lead capture as usual. After processing, update the stored state to persist conversation history and lead capture progress. 

The key benefit is that the existing agent code requires zero changes. WhatsApp provides the transport layer, the webhook server manages state persistence, and the agent handles all reasoning. Implement webhook signature validation, error handling with retries, and rate limiting for security and reliability.

### LLM Choice

Gemini 2.0 Flash is used for its low latency and availability of a free tier.

