import streamlit as st
import google.generativeai as genai
import os
import fitz  # PyMuPDF for PDF reading
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# UI
st.title("Chatbot with Gemini Flash (No Embeddings)")
uploaded_file = st.file_uploader("Upload a text or PDF file", type=["txt", "pdf"])

# Load and split document
document_chunks = []

if uploaded_file:
    # Extract text based on file type
    if uploaded_file.name.endswith(".pdf"):
        pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in pdf_doc:
            text += page.get_text()
    else:
        text = uploaded_file.read().decode("utf-8")

    # Split text into chunks
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    document_chunks = splitter.split_documents([Document(page_content=text)])
    st.success("Document loaded and split into chunks.")

# Chat input
user_input = st.text_input("Ask a question:")

if user_input and document_chunks:
    # Use all chunks as context (or limit to top N if needed)
    context = "\n".join([doc.page_content for doc in document_chunks[:5]])

    # Gemini prompt
    prompt = f"""You are a helpful assistant. Use the following context to answer the question:
    Context:
    {context}

    Question: {user_input}
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    # Display chat
    st.session_state.messages.append(("User", user_input))
    st.session_state.messages.append(("Bot", response.text))

# Show chat history
for role, msg in st.session_state.messages:
    st.markdown(f"**{role}:** {msg}")
