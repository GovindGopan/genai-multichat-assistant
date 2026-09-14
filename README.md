# GenAI Multi-Chat Assistant

A Generative AI personal assistant built with Python and Streamlit.

The application supports multiple independent conversations, persistent conversation history, short-term conversational memory, long-term user memory, semantic retrieval using embeddings, and RAG-based context injection.

## Features

* Gemini LLM integration
* Streamlit chatbot interface
* Multiple independent conversations
* Persistent conversation history using SQLite
* Create and switch between conversations
* Delete conversations
* Short-term conversation memory
* Long-term user memory
* Sentence Transformer embeddings
* ChromaDB vector database
* Semantic memory retrieval
* Retrieval-Augmented Generation (RAG)
* Basic API, database, and retrieval error handling
* Secure API-key management using environment variables

## Architecture

```text
                    User
                     |
                     v
                Streamlit UI
                     |
          +----------+----------+
          |                     |
          v                     v
   SQLite Database       Memory System
   Conversation          Sentence Transformers
   History               + ChromaDB
          |                     |
          |                     v
          |              Relevant Memories
          |                     |
          +----------+----------+
                     |
                     v
                RAG Context
                     |
                     v
                 Gemini API
                     |
                     v
                  Response
```

## Technologies

| Component             | Technology             |
| --------------------- | ---------------------- |
| Language              | Python                 |
| UI                    | Streamlit              |
| LLM                   | Google Gemini          |
| LLM SDK               | google-genai           |
| Conversation Database | SQLite                 |
| Embeddings            | Sentence Transformers  |
| Vector Database       | ChromaDB               |
| RAG                   | Custom Python pipeline |
| Version Control       | Git + GitHub           |

## Project Structure

```text
genai-multichat-assistant/
│
├── database/
│   └── database.py
│
├── memory/
│   └── memory.py
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
└── chatbot.db
```

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd genai-multichat-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the API key

Create a `.env` file:

```text
GEMINI_API_KEY=your_api_key_here
```

Never commit the `.env` file to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

## Memory Design

The application separates information into different types of memory.

### Short-Term Memory

Conversation messages are stored in SQLite and loaded for the active conversation.

### Long-Term Memory

Important user information is detected and stored as embeddings in ChromaDB.

### Retrieval

When the user asks a question, the application creates an embedding for the query and retrieves semantically relevant memories.

### RAG

Retrieved memories are added to the LLM prompt as context before generating the response.

## Current Limitation

Document upload and document-based question answering are not currently implemented. This feature can be added later using the same embedding and vector-retrieval architecture.

## Version History

* `v0.1.0` — Initial Gemini chatbot
* `v0.2.0` — Streamlit chat interface
* `v0.3.0` — SQLite conversation storage
* `v0.4.0` — Multiple conversations and short-term memory
* `v0.5.0` — Long-term user memory with embeddings and ChromaDB
* `v0.6.0` — RAG-style retrieved memory context
* `v0.7.0` — Conversation deletion
* `v0.8.0` — Error handling and dependency management
* `v1.0.0` — Final project release

