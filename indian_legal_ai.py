import streamlit as st
import openai  # We still use the OpenAI library!
from pypdf import PdfReader

# --- 🔒 CONFIGURATION ---
# 1. Paste your GROQ API Key here
GROQ_API_KEY = "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" 

# 2. Choose a Groq Model (Llama 3 is great for reasoning)
# Options: "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"
MODEL_NAME = "llama-3.3-70b-versatile"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NyayaSetu: Indian Legal AI (Groq)",
    page_icon="⚖️",
    layout="wide"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stChatInput { border-radius: 15px; }
    .law-card {
        background-color: #000000;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #b71c1c; /* Dark Red for High Court vibe */
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return str(e)

def get_groq_response(query, document_context=""):
    if not GROQ_API_KEY or "gsk_" not in GROQ_API_KEY:
        return "❌ Error: Please check your Groq API Key in line 6."

    # CONNECT TO GROQ
    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1", # <--- IMPORTANT CHANGE
        api_key=GROQ_API_KEY
    )

    system_prompt = """
    You are 'NyayaSetu', an expert Legal AI Assistant for Indian Citizens.
    
    YOUR KNOWLEDGE BASE:
    1. Constitution of India.
    2. Bharatiya Nyaya Sanhita (BNS) 2023.
    3. Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023.
    
    YOUR INSTRUCTIONS:
    1. Answer strictly based on Indian Law.
    2. Quote specific sections (e.g., "Section 69 of BNS").
    3. Be concise and practical.
    4. If a document is provided, prioritize that info.
    """

    messages = [{"role": "system", "content": system_prompt}]
    
    if document_context:
        # Groq has a smaller context window than GPT-4, so we limit text to 15,000 chars
        messages.append({"role": "system", "content": f"DOCUMENT:\n{document_context[:15000]}..."})
        messages.append({"role": "user", "content": f"Based on the document, answer: {query}"})
    else:
        messages.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME, # Using the Groq model defined at the top
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Groq Error: {str(e)}"

# --- MAIN UI ---

def main():
    with st.sidebar:
        st.title("⚡ Powered by Groq")
        uploaded_file = st.file_uploader("Upload Legal PDF", type="pdf")
        
        document_text = ""
        if uploaded_file:
            with st.spinner("Processing PDF..."):
                document_text = extract_text_from_pdf(uploaded_file)
                st.success("PDF Loaded!")

    st.title("🇮🇳 NyayaSetu (Fast AI)")
    st.markdown("Legal Assistant using **Llama 3 via Groq** (Extremely Fast).")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f"<div class='law-card'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask about Indian Law..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking at light speed..."):
                response_text = get_groq_response(prompt, document_text)
                st.markdown(f"<div class='law-card'>{response_text}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    main()