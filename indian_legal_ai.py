import streamlit as st
import openai
from pypdf import PdfReader

# --- 🔒 CONFIGURATION ---
# 1. Paste your GROQ API Key here
GROQ_API_KEY = "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" 

# 2. Choose a Groq Model
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
    .highlight {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #90caf9;
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
        return f"Error reading PDF: {str(e)}"

def call_groq_api(messages):
    """Generic function to call Groq API with a list of messages."""
    if not GROQ_API_KEY or "gsk_" not in GROQ_API_KEY:
        return "❌ Error: Invalid or missing Groq API Key."

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

    # Initialize Session State for Main Chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # --- SIDEBAR (PDF Upload) ---
    with st.sidebar:
        st.header("📂 Case Files")
        uploaded_file = st.file_uploader("Upload Legal Document (PDF)", type="pdf")
        
        document_context = ""
        if uploaded_file:
            with st.spinner("Processing Document..."):
                document_context = extract_text_from_pdf(uploaded_file)
                st.success(f"Loaded: {uploaded_file.name}")
                st.info(f"Extracted {len(document_context)} characters.")

    # --- TABS FOR DIFFERENT MODES ---
    tab1, tab2, tab3 = st.tabs(["💬 Legal Assistant", "🔄 IPC ⇄ BNS Converter", "📝 Document Drafter"])

    # ---------------------------------------------------------
    # TAB 1: STANDARD CHAT (RAG)
    # ---------------------------------------------------------
    with tab1:
        st.subheader("Ask Questions on Indian Law")
        
        # Display Chat History
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    st.markdown(f"<div class='law-card'>{message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ex: What is the punishment for cyberstalking?"):
            # 1. Add User Message to History
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # 2. Construct System Prompt
            base_system_prompt = """
            You are NyayaSetu, an elite Indian Legal Assistant. 
            Answer queries based on the Constitution, BNS 2023, BNSS 2023, and BSA 2023.
            If a document context is provided, prioritize it.
            Keep answers structured and cite sections strictly.
            """
            
            messages = [{"role": "system", "content": base_system_prompt}]
            
            if document_context:
                messages.append({"role": "system", "content": f"USER DOCUMENT CONTEXT:\n{document_context[:20000]}"})
            
            # Append entire chat history for context
            messages.extend(st.session_state.chat_history)

            # 3. Get Response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing legal precedents..."):
                    response_text = call_groq_api(messages)
                    st.markdown(f"<div class='law-card'>{response_text}</div>", unsafe_allow_html=True)
            
            # 4. Save Assistant Response
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})

   # ---------------------------------------------------------
    # TAB 2: IPC TO BNS CONVERTER (FIXED)
    # ---------------------------------------------------------
    with tab2:
        st.subheader("🔄 Legacy to New Law Converter")
        st.markdown("Use this tool to map old **IPC/CrPC** sections to the new **BNS/BNSS (2023)**.")

        col1, col2 = st.columns([1, 2])
        
        with col1:
            law_code = st.selectbox("Select Old Code", ["IPC (Indian Penal Code)", "CrPC (Criminal Procedure)", "IEA (Evidence Act)"])
            section_num = st.text_input("Enter Section Number", placeholder="e.g., 301")
            convert_btn = st.button("Analyze & Map", use_container_width=True)

        with col2:
            if convert_btn and section_num:
                with st.spinner("Searching specific legal definitions..."):
                    # --- IMPROVED PROMPT ---
                    converter_prompt = f"""
                    You are a Senior Indian Legal Expert.
                    The user wants to find the BNS/BNSS 2023 equivalent for: **{law_code} Section {section_num}**.

                    ### STRICT INSTRUCTIONS:
                    1. First, internally identify the **Legal Definition** of the old section (e.g., "IPC 300 is Murder", "IPC 420 is Cheating").
                    2. Then, find the **exact section number** in the new Bharatiya Nyaya Sanhita (BNS) or BNSS 2023 that covers this SAME definition.
                    3. **DO NOT** output generic phrases like "no direct equivalent" or "reorganized".
                    4. If the exact section number is debated, provide the section that covers the **same crime**.

                    ### EXAMPLES FOR YOUR LOGIC:
                    - IPC 302 (Punishment for Murder) -> BNS Section 103.
                    - IPC 420 (Cheating) -> BNS Section 318.
                    - IPC 124A (Sedition) -> BNS Section 152 (Acts endangering sovereignty).
                    
                    ### REQUIRED OUTPUT FORMAT:
                    **Old Law ({law_code} {section_num}):** [Brief Name/Definition]
                    **New Law (BNS/BNSS):** Section [Number] - [Name]
                    **Key Changes:** [Specific changes in prison term, fine, or definition keywords]
                    """
                    
                    messages = [{"role": "user", "content": converter_prompt}]
                    result = call_groq_api(messages)
                    
                    st.markdown(f"<div class='law-card'>{result}</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: LEGAL DRAFTER (Novelty 2)
    # ---------------------------------------------------------
    with tab3:
        st.subheader("📝 AI Legal Drafter")
        st.markdown("Generate first drafts of legal documents in seconds.")

        draft_type = st.selectbox("Document Type", ["Rental Agreement", "Affidavit", "Legal Notice", "Employment Contract", "RTI Application"])
        
        with st.form("drafting_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                party_one = st.text_input("Party 1 Name (e.g., Landlord/Employer)")
                location = st.text_input("Jurisdiction (City/State)")
            with col_b:
                party_two = st.text_input("Party 2 Name (e.g., Tenant/Employee)")
                key_terms = st.text_area("Key Terms/Details (Rent amount, notice period, specific clauses)")
            
            generate_btn = st.form_submit_button("Generate Draft")

        if generate_btn:
            if party_one and party_two and key_terms:
                with st.spinner(f"Drafting {draft_type}..."):
                    draft_prompt = f"""
                    Act as a Senior Legal Drafter in India.
                    Draft a valid **{draft_type}** for jurisdiction: {location}.
                    
                    **Parties:**
                    1. {party_one}
                    2. {party_two}
                    
                    **Terms to Include:**
                    {key_terms}
                    
                    **Instructions:**
                    - Use formal legal language.
                    - Include standard indemnity and termination clauses applicable in India.
                    - Ensure formatting is clean with placeholders [___] for dates/signatures.
                    """
                    
                    messages = [{"role": "user", "content": draft_prompt}]
                    draft_result = call_groq_api(messages)
                    
                    st.markdown(f"<div class='law-card'>{draft_result}</div>", unsafe_allow_html=True)
                    st.download_button("Download Draft", draft_result, file_name=f"{draft_type}_Draft.txt")
            else:
                st.warning("Please fill in the party names and key terms.")

if __name__ == "__main__":
    main()
