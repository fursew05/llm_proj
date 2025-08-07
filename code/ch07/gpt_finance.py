from datetime import datetime
import yfinance as yf
import pytz

def get_time(timezone : str = 'Asia/Seoul'):
    tz = pytz.timezone(timezone)
    time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    now_timezone = f'{time}{timezone}'
    print(now_timezone)
    return now_timezone

def get_finance(ticker : str):
    stock = yf.Ticker(ticker)
    info = stock.info
    print(info)
    return str(info)

def get_recommendations(ticker:str):
    stock = yf.Ticker(ticker)
    rec = stock.recommendations
    rec_md = rec.to_markdown()
    with open(f'code/ch07/output/recommendations_{ticker}','w',encoding='utf-8') as f:
        f.write(rec_md)
    print(rec_md)
    return rec_md

def get_stock_info(ticker:str,period:str = '1y'):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    hist_md = hist.to_markdown()
    print(hist_md)
    return hist_md



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
     }}},
     {"type" : "function",
      "function" : {
          "name" : "get_finance",
          "description" : "해당 종목의 yfinance info를 반환합니다.",
          "parameters" : {
              "type" : "object",
              "properties" : {
                  "ticker":{
                      "type" : "string",
                      "description" : "정보를 조회할 주식 종목 티커를 입력하세요.(예:AAPL)"
                  }
              }, "required" : ['ticker']
          }}},
    {"type" : "function",
      "function" : {
          "name" : "get_recommendations",
          "description" : "해당 종목의 전문가 의견을 반환합니다.",
          "parameters" : {
              "type" : "object",
              "properties" : {
                  "ticker":{
                      "type" : "string",
                      "description" : "정보를 조회할 주식 종목 티커를 입력하세요.(예:AAPL)"
                  }
              }, "required" : ['ticker']
          }}},
    {"type" : "function",
      "function" : {
          "name" : "get_stock_info",
          "description" : "해당 종목의 과거 주가의 ohlcv를 반환합니다.",
          "parameters" : {
              "type" : "object",
              "properties" : {
                  "ticker":{
                      "type" : "string",
                      "description" : "정보를 조회할 주식 종목 티커를 입력하세요.(예:AAPL)"
                  },
                   "period":{
                      "type" : "string",
                      "description" : "조회할 과거 기간을 입력해주세요.(예:3mo,5d,1y)"
                  }
              }, "required" : ['ticker','period']
          },
          }}
]

if __name__ == '__main__':
    get_time("America/New_York")
    get_finance("TSLA")
    get_recommendations("TSLA")
    get_stock_info("TSLA")