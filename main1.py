import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os
from google import genai

load_dotenv() 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in .env file")
    st.stop()

os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
client = genai.Client()

BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"

MODULES = {
    "Python": PROMPTS_DIR / "python.txt",
    "SQL": PROMPTS_DIR / "sql.txt",
    "Power BI": PROMPTS_DIR / "powerbi.txt",
    "EDA": PROMPTS_DIR / "eda.txt",
    "Machine Learning": PROMPTS_DIR / "ml.txt",
    "Deep Learning": PROMPTS_DIR / "dl.txt",
    "Generative AI": PROMPTS_DIR / "genai.txt",
    "Agentic AI": PROMPTS_DIR / "agenticai.txt",
}

SYSTEM_PROMPTS = {
    "Python": "You are an expert Python mentor. Explain concepts clearly...",
    "SQL": "You are an expert SQL mentor. Answer questions about queries, joins, etc.",
    "Power BI": "You are a Power BI mentor. Help with DAX, visualization, dashboards...",
    "EDA": "You are a data analysis mentor. Explain EDA techniques, visualization...",
    "Machine Learning": "You are a machine learning mentor. Explain algorithms, metrics...",
    "Deep Learning": "You are a deep learning mentor. Explain neural networks, CNNs...",
    "Generative AI": "You are a generative AI mentor. Explain LLMs, prompt engineering...",
    "Agentic AI": "You are an agentic AI mentor. Explain autonomous agents, tools..."
}

if "module" not in st.session_state:
    st.session_state.module = None

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

if st.session_state.module is None:
    st.title("AI Chatbot Mentor")
    st.write("Your personalized AI learning assistant.")
    st.write("Please select a learning module to begin:")

    selected_module = st.selectbox("Available Modules", list(MODULES.keys()))

    if st.button("Start Mentoring"):
        st.session_state.module = selected_module
        st.rerun()

else:
    module = st.session_state.module

    st.subheader(f"Welcome to {module} AI Mentor")
    st.write(f"I am your dedicated mentor for **{module}**.")

    system_prompt = SYSTEM_PROMPTS[module]

    user_input = st.text_input("Ask your question:")

    if st.button("Send") and user_input:
        chat_history = "\n".join(st.session_state.chat_log)

        full_prompt = f"""
{system_prompt}

Conversation History:
{chat_history}

User Question:
{user_input}

STRICT RULE:
If the question is NOT related to {module}, reply ONLY with:
"Sorry, I don’t know about this question. Please ask something related to the selected module."
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=full_prompt
            )
            answer = response.text.strip()

        except Exception as e:
            answer = f"[Error] {str(e)}\nPlease check your API key, plan, or quota."

        st.session_state.chat_log.append(f"User: {user_input}")
        st.session_state.chat_log.append(f"AI: {answer}")

    st.markdown("---")
    for msg in st.session_state.chat_log:
        if msg.startswith("User"):
            st.markdown(f"**{msg}**")
        else:
            st.markdown(f"🤖 {msg}")

    if st.session_state.chat_log:
        st.download_button(
            label="📥 Download Conversation",
            data="\n".join(st.session_state.chat_log),
            file_name=f"{module}_chat_history.txt",
            mime="text/plain"
        )

    if st.button("End Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
