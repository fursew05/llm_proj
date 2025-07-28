import pymupdf
import os

pdf_file_path = "C://Users//fursew//project//llm_proj//ch04//documents//한국은행 5월 경제전망보고서.pdf"
doc = pymupdf.open(pdf_file_path)

head_height = 80
foot_height = 80

full_text = ""
word_list = ['제목','목차','담당자','참고문헌','차례']
for page in doc:
    # text 밀도를 파악해서 너무 낮은 경우 건너뛰기
    if len(page.get_text().split()) < 100:
        pass
    # 제목이나 목차를 표시하는 페이지는 건너뛰기
    elif any([word in page.get_text().split() for word in word_list]) :
        pass
    else:
        rect = page.rect

        header = page.get_text(clip=(0,0,rect.width,head_height))
        footer = page.get_text(clip=(0,rect.height-foot_height,rect.width,rect.height))
        text = page.get_text(clip=(0,head_height,rect.width,rect.height-foot_height))

        # 페이지마다 줄바꿈
        full_text += text + "\n-----------------------------------------\n"

pdf_file_name = os.path.basename(pdf_file_path) # 한국은행 ~ .pdf
pdf_file_name = os.path.splitext(pdf_file_name)[0] # .pdf 사라짐

txt_file_path = f"ch04/output/{pdf_file_name}_with_preprocessing.txt"

# 저장
with open(txt_file_path,'w',encoding='utf-8') as f:
    f.write(full_text)