import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from ingest import process_documents


load_dotenv()

def build_vector_store(directory_path: str, persist_directory: str = "./chroma_db"):
    print(f"Scanning the '{directory_path}' folder for documents...")
    chunks = process_documents(directory_path)
    
    if not chunks:
        print("❌ ERROR: No text found! The PDF might be empty, a scanned image, or not in the folder.")
        return None
        
    print(f"✅ Successfully extracted {len(chunks)} text chunks. Generating embeddings...")
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    return vector_store

def test_retrieval(query: str, persist_directory: str = "./chroma_db"):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vector_store = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embeddings
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke(query)
    
    return results

if __name__ == "__main__":
    test_folder = "documents" 
    
    db = build_vector_store(test_folder)
    
    if db:
        print("🎉 Vector database built successfully with PDF data!\n")
        
        test_question = "What is the main topic of the document?"
        print(f"Testing Query: {test_question}")
        
        retrieved_docs = test_retrieval(test_question)
        
        for i, doc in enumerate(retrieved_docs):
            print(f"\n--- Result {i+1} ---")
            print(doc.page_content)