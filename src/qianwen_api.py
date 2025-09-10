import os
import dashscope
from dashscope import Generation

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


def call_qianwen(prompt, context=None):
    messages = [{'role': 'system', 'content': '你是一个儿童教育专家，用简单有趣的语言回答'}]

    if context:
        messages.append({'role': 'system', 'content': f'参考信息：{context}'})

    messages.append({'role': 'user', 'content': prompt})

    response = Generation.call(
        model='qwen-turbo',
        messages=messages,
        temperature=0.7,
        top_p=0.8
    )

    if response.status_code == 200:
        return response.output.choices[0]['message']['content']
    return "哎呀，我好像不知道怎么回答这个问题..."
