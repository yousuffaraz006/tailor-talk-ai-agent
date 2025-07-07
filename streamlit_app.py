import streamlit as st
import requests

st.title("TailorTalk AI – Book Appointments")

if "chat" not in st.session_state:
  st.session_state.chat = []

user_input = st.chat_input("Say something...")

if user_input:
  st.session_state.chat.append(("user", user_input))

  # Send message to FastAPI
  response = requests.post("http://127.0.0.1:8000/chat", json={"message": user_input})
  reply = response.json()["response"]
  st.session_state.chat.append(("bot", reply))

for sender, message in st.session_state.chat:
  with st.chat_message(sender):
    st.markdown(message)