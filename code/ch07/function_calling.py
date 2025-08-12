from gpt_finance import get_time,get_finance,get_recommendations,get_stock_info,tools
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st
from collections import defaultdict

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=api_key)

def tool_list_to_object(tools):
    tool_calls_dict = defaultdict(lambda:
                                  {"id" : None, "function" : {"arguments" : "", "name" : None}, "type" : "None"})
    for tool_call in tools:
        # id가 None이 아닐때 설정
        if tool_call.id is not None:
            tool_calls_dict[tool_call.index]["id"] = tool_call.id
        
        # Name이 None이 아닐때 설정
        if tool_call.function.name is not None:
            tool_calls_dict[tool_call.index]["function"]["name"] = tool_call.function.name
        
        # argumnets 추가
        tool_calls_dict[tool_call.index]["function"]["arguments"] += tool_call.function.arguments

        # Type이 None이 아닐때 설정
        if tool_call.type is not None:
            tool_calls_dict[tool_call.index]["type"] = tool_call.type
    
    tool_calls_list = list(tool_calls_dict.values())
    return {"tool_calls" : tool_calls_list}


def get_ai_response(messages,tools=None,stream=True):
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages=messages,
        tools = tools,
        stream = stream
    )
    if stream:
        for chunk in response:
            yield chunk
    else:
        return response


st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state['messages'] = [
        {"role" : "system", "content" : "당신은 사용자를 도와주는 상담원입니다."}
        ]
for msg in st.session_state.messages:
    if msg.get("content") and (msg['role'] == 'assistant' or msg['role'] == 'user'):
        st.chat_message(msg['role']).write(msg['content'])


if user_input := st.chat_input():
    st.session_state.messages.append(
        {'role' : "user","content" : user_input}
    )
    st.chat_message('user').write(user_input)
    ai_response = get_ai_response(messages=st.session_state['messages'],tools=tools)
    # for chunk in ai_response:
    #     print(chunk)
    # print("=================")
    tool_calls = None
    tool_calls_chunk = []
    content = ''
    
    with st.chat_message("assistant").empty():
        for chunk in ai_response:
            content_chunk = chunk.choices[0].delta.content
            if content_chunk:
                print(content_chunk,end='')
                content += content_chunk
                st.markdown(content)
            if chunk.choices[0].delta.tool_calls:
                tool_calls_chunk += chunk.choices[0].delta.tool_calls
        tool_obj = tool_list_to_object(tool_calls_chunk)
        tool_calls = tool_obj["tool_calls"]
        print(tool_calls)
        if len(tool_calls) > 0:
            print(tool_calls)
            tool_call_msg = [tool_call["function"] for tool_call in tool_calls]
            st.write(tool_call_msg)
    print('\n=================')
    print(content)

    tool_obj = tool_list_to_object(tool_calls_chunk)
    tool_calls = tool_obj["tool_calls"]
    print(tool_calls)
     
    # ai_message = ai_response.choices[0].message
    # tool_calls = ai_message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_call_id = tool_call["id"]
            arguments = json.loads(tool_call["function"]["arguments"])

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
        ai_response = get_ai_response(st.session_state.messages, tools=tools)
        content = ""
        with st.chat_message("assistant").empty():
            for chunk in ai_response:
                content_chunk = chunk.choices[0].delta.content
                if content_chunk:
                    print(content_chunk,end="")
                    content += content_chunk
                    st.markdown(content)
    st.session_state['messages'].append({"role" : "assistant", "content" : content})

    print(f"AI\t: {content}")
    # st.chat_message("assistant").write(content)
