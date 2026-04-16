import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv(find_dotenv())

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=GROQ_API_KEY,
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = PineconeVectorStore(
    index_name=PINECONE_INDEX_NAME,
    embedding=embeddings
)

def fetch_and_answer(question, chat_history=[]):
    """Retrieve from Pinecone and answer using Groq LLM with conversation history"""

    print(f"\n🔍 Question: {question}")

    try:
        # Search Pinecone for relevant chunks
        print("🔎 Searching Pinecone for relevant context...")
        docs = vectorstore.similarity_search(question, k=4)

        if not docs:
            return "I could not find any relevant information in your documents. Please make sure you have run ingest.py first."

        # Combine retrieved chunks into context
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"📊 Retrieved {len(docs)} chunks from Pinecone")

        sources = set([doc.metadata.get('source', 'Unknown') for doc in docs])
        print(f"📁 Sources: {sources}\n")

        # Format conversation history
        history_text = ""
        if chat_history:
            history_text = "Previous conversation:\n"
            for turn in chat_history:
                history_text += f"User: {turn['user']}\n"
                history_text += f"Assistant: {turn['assistant']}\n"
            history_text += "\n"

        # Generate answer using LLM
        prompt_text = f"""You are a helpful assistant. Answer the question based ONLY on the context provided below.
If the answer is not found in the context, say "I don't have enough information in my knowledge base to answer this."
Do not use any outside knowledge. Only use what is in the context.

{history_text}
Context:
{context}

Question: {question}

Answer:"""

        answer = llm.invoke(prompt_text).content
        return answer

    except Exception as e:
        print(f"❌ Error: {e}\n")
        return f"Sorry, I encountered an error: {str(e)}"

chain = fetch_and_answer