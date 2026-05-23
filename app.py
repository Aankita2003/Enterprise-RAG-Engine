import streamlit as st
from rag_pipeline import setup_rag_pipeline

st.set_page_config(page_title="Enterprise RAG Assistant", page_icon="🤖")
st.title("🤖 Enterprise Knowledge Assistant")
st.markdown("Ask me anything about the internal company documents!")

@st.cache_resource
def load_pipeline():
    return setup_rag_pipeline()

try:
    pipeline = load_pipeline()
except Exception as e:
    st.error(f"Failed to load the RAG pipeline. Error: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("What is our refund policy?"):
    with st.chat_message("user"):
        st.markdown(user_query)
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        with st.spinner("Searching internal documents..."):
            response = pipeline.invoke(user_query)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})