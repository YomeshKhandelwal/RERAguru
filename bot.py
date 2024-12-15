import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import HuggingFaceHub
import os

def app():
    # Define custom CSS for better UI/UX
    st.markdown("""
        <style>
        body {
            background-color: #f7f9fc;
            font-family: 'Helvetica Neue', sans-serif;
        }
        .main-header {
            font-size: 2.5rem;
            text-align: center;
            color: #2b6777;
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .user-bubble {
            background-color: #d1f5ff;
            padding: 15px;
            border-radius: 20px;
            margin-bottom: 15px;
            color: #005f73;
            font-weight: bold;
            width: fit-content;
            max-width: 70%;
        }
        .bot-bubble {
            background-color: #e0f7fa;
            padding: 15px;
            border-radius: 20px;
            margin-bottom: 15px;
            color: #2b6777;
            width: fit-content;
            max-width: 70%;
        }
        .chat-container {
            display: flex;
            justify-content: flex-start;
        }
        .chat-container-bot {
            justify-content: flex-end;
        }
        </style>
    """, unsafe_allow_html=True)

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    def get_pdf_text(pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", ".", " "], chunk_size=1500, chunk_overlap=500)
        chunks = text_splitter.split_text(text)
        return chunks

    def get_vectorstore(text_chunks):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore

    def get_conversation_chain(vectorstore):
        llm = HuggingFaceHub(repo_id="mistralai/Mistral-Nemo-Instruct-2407", model_kwargs={"temperature": 0.3, "max_length": 1000})
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)
        return conversation_chain

    def handle_userinput(user_question):
        # Check if user asked for context
        if "show context" in user_question.lower():
            # Show the full chat history when requested
            st.markdown("<h3>Context:</h3>", unsafe_allow_html=True)
            for i, (question, response) in enumerate(st.session_state.chat_history):
                st.markdown(f"<p><b>User:</b> {question}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><b>Bot:</b> {response}</p>", unsafe_allow_html=True)
        else:
            # Get the answer from the chain without showing context
            response = st.session_state.conversation({'question': user_question})
            
            # Add to the chat history
            st.session_state.chat_history.append((user_question, response['chat_history'][-1].content))

            # Display the latest user input and bot response
            st.markdown(f"""
                <div class="chat-container">
                    <div class="user-bubble">{user_question}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="chat-container chat-container-bot">
                    <div class="bot-bubble">{response['chat_history'][-1].content}</div>
                </div>
            """, unsafe_allow_html=True)

    # Load environment variables
    load_dotenv()

    # Sidebar for selecting the state
    with st.sidebar:
        state = st.selectbox('Select State', ['Maharashtra', 'Rajasthan'])

    # Initializing session state for conversation and chat history
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User input section
    user_question = st.text_input("Ask any question...")

    if user_question and st.session_state.conversation:
        with st.spinner("Generating response..."):
            handle_userinput(user_question)

    # Select PDF file based on the selected state
    if state == 'Maharashtra':
        pdf_docs = ["41865Judgment.pdf"]
    else:
        pdf_docs = []  # Add appropriate handling for other states

    # Ensure the PDF file exists
    if not all(os.path.isfile(pdf) for pdf in pdf_docs):
        st.error("Some PDF files are missing.")
        return

    # Process the PDF content and setup the conversation chain
    if st.session_state.conversation is None:
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        vectorstore = get_vectorstore(text_chunks)
        st.session_state.conversation = get_conversation_chain(vectorstore)

if __name__ == "__main__":
    app()
