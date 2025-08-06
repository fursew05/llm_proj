# function calling : GPT에게 원하는 함수 도구 목록을 제공하여 함수를 호출할 수 있도록 하는 기능
import pytz
from datetime import datetime

def get_time(timezone : str = 'Asia/Seoul'):
    tz = pytz.timezone(timezone)
    time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    now_timezone = f'{time}{timezone}'
    print(now_timezone)
    return now_timezone

tools = [
    {"type" : "function",
     "function" : {
         "name" : "get_time",
         "description" : "현재 시각을 반환합니다",
         "parameters":{
             "type" : "object",
             "properties":{
                 "timezone":{
                 "type" : "string",
                 "description" : "현재 날짜와 시간을 반환할 타임존을 입력하세요.(예:Asia/Seoul)"
             }
         }, "required" : ['timezone']
     }}}
]
if __name__ == '__main__':
    get_time('France/Paris')