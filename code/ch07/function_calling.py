from gpt_finance import get_time,get_finance,get_recommendations,get_stock_info,tools
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

client = OpenAI(api_key=api_key)

def get_ai_response(messages,tools=None):
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages=messages,
        tools = tools
    )
    return response


st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state['messages'] = [
        {"role" : "system", "content" : "당신은 사용자를 도와주는 상담원입니다."}
        ]
for msg in st.session_state.messages:
    if msg.get("content") and (msg['role'] == 'assistant' or msg['role'] == 'user'):
        st.chat_message(msg['role']).write(msg['content'])

# for i, msg in enumerate(st.session_state["messages"]):
#     if msg.get("content") is None:
#         st.write(f"🔍 메시지 {i}번: content가 None입니다.")
#         st.json(msg)

if user_input := st.chat_input():
    st.session_state.messages.append(
        {'role' : "user","content" : user_input}
    )
    st.chat_message('user').write(user_input)

    # st.session_state['messages'].append({"role" : "user","content" : user_input})
    
    # ✅ 디버깅: content가 None인 메시지 출력
    for i, msg in enumerate(st.session_state["messages"]):
        if msg.get("content") is None:
            print(f"[DEBUG] 메시지 {i}번: content가 None입니다.")
            print(msg)
            st.write(f"🛠 메시지 {i}번: content가 None입니다.")
            st.json(msg)


    ai_response = get_ai_response(messages=st.session_state['messages'],tools=tools)
    ai_message = ai_response.choices[0].message
    print(ai_message)

    tool_calls = ai_message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id
            arguments = json.loads(tool_call.function.arguments)

            if tool_name == "get_time":
                called_func = get_time(timezone=arguments['timezone'])
            elif tool_name == "get_finance":
                called_func = get_finance(ticker=arguments['ticker'])
            elif tool_name == "get_recommendations":
                called_func = get_recommendations(ticker = arguments['ticker'])
            elif tool_name == "get_stock_info":
                called_func = get_stock_info(ticker = arguments['ticker'], period = arguments['period'])

            st.session_state['messages'].append({
                "role" : "function",
                "tool_call_id" : tool_call_id,
                "name" : tool_name,
                "content" : called_func
            })

        st.session_state['messages'].append({'role' : 'system','content' : '이제 주어진 결과를 바탕으로 답변할 차례입니다.'})

        ai_response = get_ai_response(messages=st.session_state['messages'],tools=tools)
        ai_message = ai_response.choices[0].message
    st.session_state['messages'].append({"role" : "assistant", "content" : ai_message.content})

    print(f"AI\t: {ai_message.content}")
    st.chat_message("assistant").write(ai_message.content)
