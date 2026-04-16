# Private Data RAG Assistant using Langchain, Pinecone, HuggingFace RAG and Groq LLM. Completely Free

> A conversational AI that answers questions **exclusively from your own given data** — no outside knowledge, just your data.
---
## Quick Start
### 1. Clone the repository
git clone https://github.com/MuhammadAqibb/RAG-Using-langchain-pinecone-and-Gorq-LLM.git
cd your-repo-name
### 2. Install dependencies
pip install -r requirements.txt
### 3. Set up your API keys
Rename `.env.example` to `.env` and fill in your keys:

GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
#### 4. Add your documents
Drop your PDF or TXT files into the `data/` folder.
#### 5. Ingest your data
python ingest.py
> Only needs to be run once, or whenever you add new documents.
#### 6. Start the app
uvicorn server:app

#### 7. Open your browser
Go to **http://localhost:8000** and start asking questions!

## Tech Stack & Why Each Tool Was Used

| Tool | Purpose | Why It Matters |
|------|---------|----------------|
| **FastAPI** | Web server & API | Fast, modern Python web framework. Serves the chat UI and handles requests |
| **Groq + LLaMA 3.3 70B** | Language Model | Extremely fast inference. Generates accurate, context-aware answers |
| **Pinecone** | Vector Database | Stores document embeddings in the cloud. Enables fast semantic search across your data |
| **HuggingFace Embeddings** | Text → Vectors | Converts text into numerical representations so documents can be searched by meaning |
| **LangChain** | RAG Framework | Connects all the components together — loaders, splitters, embeddings, and retrieval |
| **sentence-transformers/all-MiniLM-L6-v2** | Embedding Model | Lightweight but powerful model that converts text chunks into searchable vectors |
| **PyMuPDF** | PDF Loader | Reliably extracts text from complex PDF documents |
| **python-dotenv** | Config Management | Keeps API keys safe and out of your codebase |


## Full Project Pipeline

Your Documents (PDF / TXT)
          │
          ▼
   Load with PyMuPDF / TextLoader
          │
          ▼
   Split into 500-word chunks
   (with 50-word overlap)
          │
          ▼
   Convert chunks to Embeddings
   (HuggingFace all-MiniLM-L6-v2)
          │
          ▼
   Store Embeddings in Pinecone
   ──────────────────────────────
   (Ingestion is done. App is ready.)
   ──────────────────────────────
          │
   User asks a Question
          │
          ▼
   Question → converted to Embedding
          │
          ▼
   Pinecone searches for most
   similar chunks (Top 4)
          │
          ▼
   Relevant chunks + Question
   sent to Groq LLaMA 3.3 70B
          │
          ▼
   LLM answers based ONLY
   on retrieved chunks
          │
          ▼
   Answer displayed in Chat UI

## 💡 How It Works

This project uses **RAG (Retrieval Augmented Generation)** — a technique that grounds the LLM's answers in your specific documents instead of its general training data.

There are two phases:
**Ingestion Phase** (run once)
- Your documents are loaded, split into chunks, converted into vectors, and stored in Pinecone.
**Query Phase** (every question)
- Your question is converted into a vector, Pinecone finds the most relevant chunks, and the LLM uses only those chunks to generate an answer.
This means the LLM will never make up information — if the answer isn't in your documents, it will say so.

## 🔮 Future Use Cases
### Business & Enterprise
- **Internal knowledge base** — employees can query company policies, handbooks, and SOPs instantly
- **Legal document assistant** — query contracts, case files, and legal briefs
- **Medical records assistant** — search patient records or medical literature privately
- **Customer support bot** — answer customer questions from your product documentation
### Education
- **Study assistant** — upload your textbooks and lecture notes, ask exam questions
- **Research assistant** — query multiple research papers and get synthesized answers
- **Course Q&A bot** — students ask questions, answered from course material only
### Personal Use
- **Personal finance assistant** — upload your financial statements and ask questions
- **Book notes assistant** — upload your highlights and summaries, query them conversationally
- **Recipe assistant** — upload your recipe collection and search by ingredient or cuisine
---
## 🔌 Possible Extensions
- **Multi-user support** — add user authentication so each user has their own private history
- **Persistent chat history** — store conversations in a database (SQLite or PostgreSQL)
- **Source citations** — show which document and page number each answer came from
- **Multiple file formats** — add support for Word documents, CSVs, and web scraping
- **Re-ingestion detection** — automatically detect and re-ingest changed documents
- **Streaming responses** — stream the LLM response word by word for a better UX
- **Second project** — connect to the pre-built Wikipedia Pinecone dataset for a general knowledge assistant

## 📁 Project Structure
my-rag-app/
│
├── data/                  ← Add your PDF and TXT files here
├── ingest.py              ← Run once to load documents into Pinecone
├── chain.py               ← RAG logic: retrieval + LLM answering
├── server.py              ← FastAPI server + chat UI
├── .env                   ← Your API keys (never commit this)
├── .env.example           ← Template for required environment variables
├── .gitignore             ← Keeps data and .env off GitHub
└── requirements.txt       ← Python dependencies

## 🔑 Getting Your API Keys
- **Groq API Key** → [console.groq.com](https://console.groq.com)
- **Pinecone API Key** → [app.pinecone.io](https://app.pinecone.io)
