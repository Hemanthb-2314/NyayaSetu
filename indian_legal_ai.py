import streamlit as st
import openai
from pypdf import PdfReader

# --- 🔒 CONFIGURATION ---
# Using Streamlit Secrets for security (Set 'GROQ_API_KEY' in Streamlit Cloud Dashboard)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    # Fallback for local testing (only works if you have a .streamlit/secrets.toml)
    GROQ_API_KEY = ""

MODEL_NAME = "llama-3.3-70b-versatile"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NyayaSetu Pro: Indian Legal Suite",
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
        color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #b71c1c;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .stInfo { border-radius: 10px; }
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
        return f"Error reading PDF: {str(e)}"

def call_groq_api(messages):
    if not GROQ_API_KEY:
        return "❌ Error: API Key not found. Please add 'GROQ_API_KEY' to Streamlit Secrets."

    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Groq API Error: {str(e)}"

# --- MAIN UI ---

def main():
    st.title("⚖️ NyayaSetu Pro")
    st.markdown("### Indian Legal Intelligence Suite")

    # Initialize Session State
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("📂 Case Files")
        uploaded_file = st.file_uploader("Upload Legal Document (PDF)", type="pdf")
        
        document_context = ""
        if uploaded_file:
            with st.spinner("Processing Document..."):
                document_context = extract_text_from_pdf(uploaded_file)
                st.success(f"Loaded: {uploaded_file.name}")
        
        st.divider()
        st.header("⚙️ Settings")
        
        # THE TOGGLE: Default to New Law (BNS)
        law_mode = st.toggle("Switch to New Laws (BNS 2023)", value=True, 
                             help="When ON, responses prioritize Bharatiya Nyaya Sanhita. When OFF, responses use IPC.")
        
        current_framework = "BNS 2023" if law_mode else "IPC 1860"
        st.info(f"Mode: **{current_framework}**")
        
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["💬 Legal Assistant", "🔄 IPC ⇄ BNS Converter", "📝 Document Drafter"])

    # TAB 1: LEGAL CHAT
    with tab1:
        st.subheader(f"Chatting in {current_framework} Mode")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    st.markdown(f"<div class='law-card'>{message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ex: What is the punishment for cheating?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # --- DYNAMIC PROMPT LOGIC ---
            if law_mode:
                framework_instruction = "You MUST use the Bharatiya Nyaya Sanhita (BNS) 2023. If the user mentions old IPC sections, correct them to the new BNS sections."
            else:
                framework_instruction = "You MUST use the legacy Indian Penal Code (IPC) 1860. Focus on the traditional sections used before 2023."

            base_system_prompt = f"""
            You are NyayaSetu, an elite Indian Legal Assistant. 
            CURRENT FRAMEWORK: {framework_instruction}
            If a document context is provided, prioritize it.
            Keep answers structured and cite sections strictly.
            """
            
            messages = [{"role": "system", "content": base_system_prompt}]
            if document_context:
                messages.append({"role": "system", "content": f"USER DOCUMENT CONTEXT:\n{document_context[:15000]}"})
            
            messages.extend(st.session_state.chat_history)

            with st.chat_message("assistant"):
                with st.spinner(f"Consulting {current_framework}..."):
                    response_text = call_groq_api(messages)
                    st.markdown(f"<div class='law-card'>{response_text}</div>", unsafe_allow_html=True)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})

    # TAB 2: CONVERTER
    with tab2:
        st.subheader("🔄 Legacy to New Law Converter")
        col1, col2 = st.columns([1, 2])
        with col1:
            law_code = st.selectbox("Select Old Code", ["IPC", "CrPC", "IEA"])
            section_num = st.text_input("Enter Section Number", placeholder="e.g., 420")
            convert_btn = st.button("Analyze & Map", use_container_width=True)
        with col2:
            if convert_btn and section_num:
                converter_prompt = f"Map {law_code} Section {section_num} to the new 2023 Laws (BNS/BNSS/BSA). Provide Section Number, Definition, and Key Changes."
                result = call_groq_api([{"role": "user", "content": converter_prompt}])
                st.markdown(f"<div class='law-card'>{result}</div>", unsafe_allow_html=True)

    # TAB 3: DRAFTER
    with tab3:
        st.subheader("📝 AI Legal Drafter")
        draft_type = st.selectbox("Document Type", ["Rental Agreement", "Affidavit", "Legal Notice", "Employment Contract"])
        with st.form("drafting_form"):
            p1 = st.text_input("Party 1 Name")
            p2 = st.text_input("Party 2 Name")
            loc = st.text_input("Jurisdiction")
            terms = st.text_area("Key Terms")
            submit = st.form_submit_button("Generate Draft")
        
        if submit and p1 and p2:
            draft_prompt = f"Draft a {draft_type} between {p1} and {p2} in {loc}. Include: {terms}. Use formal Indian legal language."
            draft = call_groq_api([{"role": "user", "content": draft_prompt}])
            st.markdown(f"<div class='law-card'>{draft}</div>", unsafe_allow_html=True)
            st.download_button("Download Draft", draft, file_name=f"{draft_type}.txt")

if __name__ == "__main__":
    main()
