import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
import time

# -----------------------------
# Load API keys securely from Streamlit Secrets
# -----------------------------
# Add in Streamlit Secrets:
# GROQ_API_KEY = "your_groq_key_here"
# OPENAI_API_KEY = "your_openai_key_here"
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

groq_api_key = os.environ["GROQ_API_KEY"]

# -----------------------------
# Initialize Groq LLM
# -----------------------------
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

# -----------------------------
# Define prompt template
# -----------------------------
prompt = ChatPromptTemplate.from_template(
    """ 
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    <context>
    Question: {input}
    """
)

# -----------------------------
# Function to create vector embeddings
# -----------------------------
def create_vector_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = OpenAIEmbeddings()  # uses OpenAI key
        st.session_state.loader = PyPDFDirectoryLoader("research_papers")
        st.session_state.docs = st.session_state.loader.load()
        st.write(f"Loaded {len(st.session_state.docs)} documents")

        if len(st.session_state.docs) == 0:
            st.error("No PDF documents found in 'research_papers' folder.")
            return

        st.session_state.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # smaller chunks to ensure splitting
            chunk_overlap=300
        )
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(
            st.session_state.docs[:50]
        )
        st.write(f"Total document chunks: {len(st.session_state.final_documents)}")

        if len(st.session_state.final_documents) == 0:
            st.error("No document chunks created. Check PDF content or chunk size.")
            return

        st.session_state.vectors = FAISS.from_documents(
            st.session_state.final_documents, st.session_state.embeddings
        )
        st.success("Vector database created successfully!")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("RAG Document Q&A With Groq And LLaMA3")

# User query input
user_prompt = st.text_input("Enter your query from the research papers")

# Button to create vector DB
if st.button("Create Document Embeddings"):
    create_vector_embedding()

# Generate summary if query exists
if user_prompt and "vectors" in st.session_state:
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    start = time.process_time()
    response = retrieval_chain.invoke({'input': user_prompt})
    st.write(f"Response time: {time.process_time() - start:.2f} seconds")

    # Editable summary
    editable_summary = st.text_area(
        "Generated Summary (Editable)", 
        value=response['answer'], 
        height=200
    )

    # Optional: show document chunks
    with st.expander("Document similarity search"):
        for i, doc in enumerate(response['context']):
            st.write(doc.page_content)
            st.write('--------')
