
import os
import warnings
import streamlit as st
from dotenv import load_dotenv
from agent.state import AgentState
from agent.graph import agent_step

# Suppress SSL warnings from gRPC
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings('ignore', category=UserWarning)

# Load environment variables from a local .env file (e.g., GOOGLE_API_KEY)
# override=True ensures .env file takes precedence over system environment variables
load_dotenv(override=True)

st.set_page_config(page_title="AutoStream AI Agent")

if "state" not in st.session_state:
    st.session_state.state = AgentState()
    st.session_state.chat = []

st.title("🤖 AutoStream Conversational AI (Gemini)")

user_input = st.text_input("You:", key="input")

if st.button("Send") and user_input:
    state = st.session_state.state
    response = agent_step(state, user_input)
    st.session_state.chat.append(("User", user_input))
    st.session_state.chat.append(("Agent", response))

for sender, msg in st.session_state.chat:
    st.write(f"**{sender}:** {msg}")
