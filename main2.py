import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

st.title('Simple Chatbot with OpenAI API')

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }, 
        {
            "role": "assistant",
            "content": "무엇을 도와드릴까요?"
        }
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input():
    st.chat_message("user").write(prompt)

    
    client = OpenAI(api_key=api_key)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state["messages"]
    )
    msg = response.choices[0].message.content

    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)