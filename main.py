from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse  # Required for word-by-word streaming
from pydantic import BaseModel
from typing import List
import os
import shutil
import traceback

from langchain_core.messages import HumanMessage, AIMessage
from rag_pipeline import setup_rag_pipeline
from vector_store import build_vector_store

# 1. Initialize the App
app = FastAPI(title="Enterprise RAG Engine Gateway")

# 2. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Load Pipeline
pipeline = setup_rag_pipeline()

# 4. Define Data Models
class MessageDict(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    question: str
    chat_history: List[MessageDict] = []

class QueryResponse(BaseModel):
    answer: str

# 5. Define Endpoints

# --- STREAMING QUERY ENDPOINT ---
@app.post("/api/v1/query")
async def execute_rag_query(request: QueryRequest):
    try:
        print(f"\n--- Received Streaming Question: {request.question} ---")
        
        # 1. Format the history
        formatted_history = []
        for msg in request.chat_history:
            if msg.role == "user":
                formatted_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                formatted_history.append(AIMessage(content=msg.content))
                
        # 2. Create an async generator that yields words as they are generated
        async def generate_response():
            try:
                # We use .astream() instead of .invoke()
                async for chunk in pipeline.astream({
                    "input": request.question,
                    "chat_history": formatted_history
                }):
                    yield chunk
            except Exception as e:
                yield f"Error generating response: {str(e)}"

        # 3. Return the open stream pipe
        return StreamingResponse(generate_response(), media_type="text/plain")
        
    except Exception as exc:
        print("\n❌ CRITICAL PIPELINE ERROR ❌")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


# --- FILE UPLOAD ENDPOINT ---
@app.post("/api/v1/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Ensure the documents directory exists
        os.makedirs("documents", exist_ok=True)
        
        # Save the uploaded file
        file_path = f"documents/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Rebuild the vector database with the new document
        build_vector_store("documents")
        
        # Reload the pipeline in memory so it sees the new data
        global pipeline
        pipeline = setup_rag_pipeline()
        
        return {"message": f"Successfully uploaded and processed: {file.filename}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))