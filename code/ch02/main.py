import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

with st.sidebar:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    "[API KEY 발급](https://platform.openai.com/account/api-keys)"
    "[소스코드 보기](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![깃허브에서 열기](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("Chat GPT를 활용한 챗봇")

if "messages" not in st.session_state:
    st.session_state['messages'] = [{"role" : "assistant", "content" : "무엇을 도와드릴까요?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input():
    # 유저 메시지 저장 및 출력
    st.chat_message("user").write(prompt)
    # 모델 호출
    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages
    )
    msg = response.choices[0].message.content

    # 모델 메시지 저장 및 출력
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

