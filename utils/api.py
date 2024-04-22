import openai
from openai import OpenAI
import httpx

OPENAI_API_KEY='...'
client = OpenAI(api_key=OPENAI_API_KEY)

def chatgpt(query):
    query_session = [{"role":"user", "content": query}]
    resp = client.chat.completions.create(
        model='gpt-4-1106-preview',
        messages=query_session,
        temperature=0.1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    ret = resp.choices[0].message.content
    return ret

if __name__ == '__main__':
    print((chatgpt('怎么用python代码计算第100个质数？')))