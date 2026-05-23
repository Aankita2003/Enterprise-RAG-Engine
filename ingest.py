import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

def process_documents(directory_path):
    loader = PyPDFDirectoryLoader(directory_path)
    raw_documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    chunked_documents = text_splitter.split_documents(raw_documents)
    
    return chunked_documents

if __name__ == "__main__":
    folder_path = "documents" 
    
    try:
        chunks = process_documents(folder_path)
        print(f"Successfully generated {len(chunks)} chunks.")
        
        if chunks:
            print("\nPreview of Chunk 1:")
            print("-" * 40)
            print(chunks[0].page_content)
            print("-" * 40)
            print(f"Metadata: {chunks[0].metadata}")
            
    except Exception as e:
        print(f"Error processing document: {e}")