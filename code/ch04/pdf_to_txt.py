import pymupdf
import os

pdf_file_path = "C:\\Users\\fursew\\project\\llm_proj\\ch04\\documents\\한국은행 5월 경제전망보고서.pdf"
doc = pymupdf.open(pdf_file_path)

full_text = ""

# doc는 iterable 객체임, 반복문을 활용하여 페이지마다 텍스트를 추출
for page in doc:
    text = page.get_text()
    full_text += text

pdf_file_name = os.path.basename(pdf_file_path) # 한국은행 ~ .pdf
pdf_file_name = os.path.splitext(pdf_file_name)[0] # .pdf 사라짐

txt_file_path = f"ch04/output/{pdf_file_name}.txt"

# 저장
with open(txt_file_path,'w',encoding='utf-8') as f:
    f.write(full_text)