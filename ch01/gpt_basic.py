from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model = 'gpt-4o',
    temperature = 0.1,
    messages = [{"role" : "system", "content" : "You are a helpful assistant."},
                {"role" : "user", "content" : "지난 월드컵 우승국은 어딘가요?"}]
)

print(response)

print("----")
print(response.choices[0].message.content)