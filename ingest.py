import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

def ingest_data():
    print("Loading your documents...")

    data_folder = "data"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        print(f"Created '{data_folder}' folder. Please add your PDF or TXT files there and run again.")
        return

    documents = []
    for file in os.listdir(data_folder):
        filepath = os.path.join(data_folder, file)
        
        try:
            if file.endswith(".pdf"):
                print(f"Loading PDF: {file}")
                # Switched to PyMuPDFLoader for better stability with complex PDFs
                loader = PyMuPDFLoader(filepath)
                documents.extend(loader.load())
            elif file.endswith(".txt"):
                print(f"Loading TXT: {file}")
                loader = TextLoader(filepath, encoding="utf-8")
                documents.extend(loader.load())
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
            print("Skipping this file and continuing...")

    if not documents:
        print("No documents found or all documents failed to load.")
        return

    print(f"✅ Successfully loaded {len(documents)} pages/documents")

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")

    # Create embeddings
    # Note: This will download the model (approx 80MB) on the first run
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Store in Pinecone
    index_name = os.getenv("PINECONE_INDEX_NAME")
    if not index_name:
        print("❌ Error: PINECONE_INDEX_NAME not found in .env file.")
        return

    print(f"Storing in Pinecone index: {index_name}...")
    try:
        PineconeVectorStore.from_documents(chunks, embeddings, index_name=index_name)
        print("✅ Success! Your data is now in Pinecone.")
    except Exception as e:
        print(f"❌ Error uploading to Pinecone: {e}")

if __name__ == "__main__":
    ingest_data()