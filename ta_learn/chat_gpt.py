import openai
from dotenv import dotenv_values
config = {
    **dotenv_values("../.env")
}
# 使用您的 OpenAI 密钥初始化 OpenAI 库
openai.api_key = config['OPENAI_API_KEY']

# 创建一个 GPT-3 模型实例
model = openai.Completion.create(
    engine="text-davinci-002",
    prompt="Hello, I am GPT-3. How can I help you?",
    temperature=0.5,
    max_tokens=1024,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
)

# 获取 GPT-3 模型的响应
response = model.get_response()

# 打印响应
print(response)
