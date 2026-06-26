import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="AI Mental Health Therapist", layout="wide")
st.title("🧠 SafeSpace – AI Mental Health Therapist")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("What's on your mind today?")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    try:
        response = requests.post(BACKEND_URL, json={"message": user_input}, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            reply = f'{data["response"]} WITH TOOL: [{data["tool_called"]}]'
        else:
            reply = f"Server returned error {response.status_code}. Please try again."

    except requests.exceptions.ConnectionError:
        reply = "Cannot connect to backend. Make sure main.py is running."
    except requests.exceptions.Timeout:
        reply = "Request timed out. MedGemma may be slow. Please try again."
    except Exception as e:
        reply = f"Unexpected error: {e}"

    st.session_state.chat_history.append({"role": "assistant", "content": reply})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])