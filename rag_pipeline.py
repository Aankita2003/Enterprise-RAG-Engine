import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def setup_rag_pipeline(persist_directory: str = "./chroma_db"):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    llm = ChatOllama(model="llama3.2", temperature=0.0)

    # 1. AI Prompt to rewrite the question based on previous chat history
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    
    # 2. Main Q&A Prompt
    system_prompt = (
        "You are an intelligent internal assistant for our company. "
        "Use the following pieces of retrieved context to answer the user's question. "
        "If the answer is not contained within the context, politely say that you do not know. "
        "Do not make up information.\n\n"
        "Context:\n{context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Logic to route the question
    def get_question(input_dict):
        if not input_dict.get("chat_history"):
            return input_dict["input"]
        # If there is history, use the LLM to rewrite the question first
        rewrite_chain = contextualize_q_prompt | llm | StrOutputParser()
        return rewrite_chain.invoke(input_dict)

    # 3. The unified conversational chain
    rag_chain = (
        RunnablePassthrough.assign(
            context=get_question | retriever | format_docs
        )
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain