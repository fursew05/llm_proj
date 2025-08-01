# from openai import OpenAI
# import os
# from dotenv import load_dotenv

# load_dotenv()

# api_key = os.getenv("OPEN_API_KEY")

# # txt 파일을 요약하는 함수 만들기
# def summarize_txt(txt_file_path):
#     client = OpenAI(api_key=api_key)

#     with open(txt_file_path,'r',encoding='utf-8') as f:
#         txt = f.read()
    
#     system_prompt = """당신은 다음의 글을 요약해주는 기계입니다. 아래의 글을 읽고 최근 경제 동향과 주장을 파악하고 주요 내용을
#     요약해 주세요. 출력 형식은 다음과 같이 해주세요.

#     ## 제목

#     ## 작성자의 문제 인식 및 주장(20문장 이내)

#     ## 텍스트에 대한 요약

#     =======================이하 텍스트=========================
#     """
#     print(system_prompt)
#     print("="*30)

#     response = client.chat.completions.create(
#         model = 'gpt-4o',
#         temperature = 0.1,
#         messages = [
#             {"role":"system",'content':system_prompt},
#         ]
#     )
#     return response.choices[0].message.content

# if __name__ == "__main__":
#     file_path = "C://Users//fursew//project//llm_proj//ch04//output//한국은행 5월 경제전망보고서_with_preprocessing.txt"
#     summary = summarize_txt(file_path)
    
#     with open("ch04/output/summary.txt","w",encoding='utf-8') as f:
#         f.write(summary)

from openai import OpenAI
import os
from dotenv import load_dotenv
import tiktoken

load_dotenv()
api_key = os.getenv("LLAMA_KEY")
client = OpenAI(base_url='http://127.0.0.1:8080/v1', api_key=api_key)

# 최대 입력 토큰 수 제한
MAX_INPUT_TOKENS = 7000  # gpt-4o는 최대 128k지만 TPM제한 고려

# 텍스트를 토큰 수 기준으로 분할
def split_text_by_tokens(text, max_tokens=MAX_INPUT_TOKENS, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)
    words = text.split()
    chunks = []
    chunk = []
    token_count = 0

    # max_tokens를 초과하지 않는 청크 생성
    for word in words:
        word_tokens = len(encoding.encode(word + " "))
        if token_count + word_tokens > max_tokens:
            chunks.append(" ".join(chunk))
            chunk = [word]
            token_count = word_tokens
        else:
            chunk.append(word)
            token_count += word_tokens
    
    # 청크들 결합
    if chunk:
        chunks.append(" ".join(chunk))

    return chunks

# 개별 chunk 요약 함수
def summarize_chunk(text_chunk):
    system_prompt = """당신은 다음의 글을 요약해주는 기계입니다. 아래의 글을 읽고 최근 경제 동향과 주장을 파악하고 주요 내용을 요약해 주세요.
출력 형식은 다음과 같이 해주세요.

## 제목

## 작성자의 문제 인식 및 주장(20문장 이내)

## 텍스트에 대한 요약

=======================이하 텍스트=========================
"""
    full_prompt = system_prompt + text_chunk

    response = client.chat.completions.create(
        model='Qwen-8B-GGUF',
        temperature=0.1,
        messages=[
            {"role": "system", "content": full_prompt + "/no_think"}
        ]
    )

    return response.choices[0].message.content

# 전체 요약 파이프라인
def summarize_txt(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    text_chunks = split_text_by_tokens(full_text)

    summaries = []
    for idx, chunk in enumerate(text_chunks):
        print(f"⏳ Chunk {idx+1}/{len(text_chunks)} 요약 중...")
        summary = summarize_chunk(chunk)
        summaries.append(summary)

    print("✅ 부분 요약 완료. 최종 통합 요약 생성 중...")

    # 부분 요약들 하나로 합쳐서 최종 요약
    combined_summary = "\n\n".join(summaries)
    final_summary = summarize_chunk(combined_summary)  # 통합 요약도 한번 더 요약

    return final_summary

# 실행부
if __name__ == "__main__":
    file_path = r"C:\Users\fursew\project\open_ai\code\ch04\output\한국은행 5월 경제전망보고서_with_preprocessing.txt"
    summary = summarize_txt(file_path)

    with open("ch04/output/summary.txt", "w", encoding='utf-8') as f:
        f.write(summary)
