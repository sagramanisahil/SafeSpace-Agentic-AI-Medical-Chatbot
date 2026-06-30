# 🧠 SafeSpace — Agentic AI Mental Health Companion

> An autonomous, tool-using AI agent for mental health support — built with LangGraph, MedGemma, and real-world action-taking via Twilio.

SafeSpace isn't a typical chatbot wrapper around an LLM. It's an **agent**: a system that reasons about a conversation, decides which tool (if any) it needs, and acts — including placing a real emergency phone call autonomously when it detects suicidal ideation, with zero human in the loop.

---

## Table of Contents
- [Problem & Motivation](#-problem--motivation)
- [What It Does](#-what-it-does)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Challenges Faced](#-challenges-faced)
- [Setup Guide](#-setup-guide)
- [Project Structure](#-project-structure)
- [Important Disclaimer](#-important-disclaimer)
- [Roadmap](#-roadmap)
- [Acknowledgements](#-acknowledgements)

---

## Problem & Motivation

Most "AI mental health chatbots" out there are single-turn Q&A systems — you type a message, an LLM generates a sympathetic-sounding reply, and that's it. There's no memory, no real-world awareness, and critically, **no ability to act**. If someone expresses a genuine crisis, the chatbot just... keeps chatting.

I built SafeSpace as a deep-dive into **agentic AI architecture** — going beyond prompt-response patterns into a system that:
- Maintains context across a multi-turn conversation
- Reasons about *what kind of help* a user actually needs at each turn
- Has access to real tools (not just text generation) and decides autonomously when to invoke them
- Can take an irreversible, high-stakes action (an emergency call) when the situation genuinely warrants it

This project was built primarily as a **technical showcase of production-grade agentic AI engineering** — the kind of reasoning → tool-routing → action pipeline that's increasingly relevant for real-world AI systems beyond just mental health.

---

## What It Does

| Capability | Description |
|---|---|
| Therapeutic conversation | Empathetic, context-aware responses powered by **MedGemma** running locally via **Ollama** |
| Multi-turn memory | Conversation state persists across turns so the agent has full context, not just the last message |
| Crisis detection & emergency call | When suicidal ideation is detected, the agent autonomously calls a real phone number via **Twilio Voice API** — no human approval step |
| Therapist finder | Location-aware tool that surfaces nearby mental health professionals |
| Agentic tool routing | Built on **LangGraph's ReAct pattern** — the agent decides *which* of its 3 tools to call (or none) based on reasoning over the conversation |

---

## Architecture

```
                 ┌─────────────────────┐
                 │   User Message       │
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │   FastAPI Backend     │
                 │  (session + memory)   │
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │  LangGraph ReAct      │
                 │  Agent (reasoning)    │
                 └──────────┬───────────┘
              ┌─────────────┼─────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
     │ MedGemma       │ │ Twilio Call    │ │ Therapist Finder   │
     │ (Ollama)       │ │ Tool           │ │ (location-based)   │
     │ therapeutic    │ │ crisis         │ │ tool                │
     │ response       │ │ escalation     │ │                     │
     └──────────────┘ └──────────────┘ └──────────────────┘
```

The agent loop follows the **ReAct (Reason + Act)** pattern: at every turn, the LLM reasons about the user's state, decides whether a tool call is needed, executes it if so, observes the result, and produces a final response — all orchestrated through LangGraph's graph-based state machine rather than a hardcoded if/else chain.

---

## Tech Stack

- **Agent Framework:** [LangGraph](https://www.langchain.com/langgraph) (ReAct architecture)
- **LLM:** MedGemma, served locally via [Ollama](https://ollama.com/)
- **Backend:** FastAPI (Python) — structured tool routing, multi-turn conversation memory
- **Telephony:** Twilio Voice API (autonomous emergency calling)
- **Location Services:** Geolocation-based therapist search tool
- **Language:** Python 3.10+

---

## Challenges Faced

The hardest part of this project wasn't the agent logic — it was getting **MedGemma running well and responding fast through Ollama**.

- Local inference introduced latency that doesn't show up when prototyping against hosted APIs — every extra second matters in a conversational UX, especially one dealing with sensitive topics.
- Tuning Ollama's runtime (context window size, model quantization, concurrent request handling) to balance response quality against speed took significant iteration.
- Keeping response latency acceptable while still preserving full multi-turn conversation context (which grows the prompt size each turn) required careful trimming/summarization of conversation history rather than naively appending every prior turn.

This pushed me to think seriously about the tradeoffs between local/open models (privacy, cost, control) vs. hosted APIs (latency, ease) — a tradeoff that's very real in production agentic systems.

---

## Setup Guide

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/download) installed locally
- A Twilio account (Account SID, Auth Token, and a verified phone number)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/sagramanisahil/SafeSpace-Agentic-AI-Medical-Chatbot.git
cd SafeSpace-Agentic-AI-Medical-Chatbot
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Pull the MedGemma model via Ollama
```bash
ollama pull medgemma
```
Make sure the Ollama service is running in the background:
```bash
ollama serve
```

### 5. Configure environment variables
Create a `.env` file in the project root:
```env
OLLAMA_BASE_URL=http://localhost:11434
MEDGEMMA_MODEL=medgemma

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number
EMERGENCY_CONTACT_NUMBER=number_to_call_on_crisis_detection

LOCATION_API_KEY=your_location_service_api_key
```

### 6. Run the FastAPI backend
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

### 7. Test it
Use the interactive API docs at `http://localhost:8000/docs` to send a test message, or hit the chat endpoint directly with `curl` / Postman.

Be careful when testing crisis-detection flows — the Twilio call trigger is real and will place an actual phone call if configured with live credentials.

---

## Project Structure
```
SafeSpace-Agentic-AI-Medical-Chatbot/
├── app/
│   ├── agent/              # LangGraph ReAct agent + tool definitions
│   ├── tools/               # MedGemma, Twilio, therapist-finder tools
│   ├── api/                 # FastAPI routes
│   └── memory/               # Conversation memory handling
├── requirements.txt
├── .env.example
└── README.md
```
*(Adjust to match your actual repo layout.)*

---

## Important Disclaimer

SafeSpace is a **personal/portfolio project built to demonstrate agentic AI engineering**, not a clinically validated medical or mental health product. It is not a replacement for professional mental health care, and it has not undergone clinical testing or regulatory review.

If you or someone you know is in crisis, please contact a licensed mental health professional or your local emergency services directly. In the US, you can call or text **988** (Suicide & Crisis Lifeline).

---

## Roadmap
- [ ] Add evaluation suite for crisis-detection precision/recall
- [ ] Support additional LLM backends (swap MedGemma for other open models)
- [ ] Web-based chat UI
- [ ] Conversation summarization for longer-term memory efficiency

---

## Acknowledgements
Built using LangGraph, Ollama, MedGemma, and the Twilio Voice API.

---

⭐ If you found this project interesting, consider starring the repo!
