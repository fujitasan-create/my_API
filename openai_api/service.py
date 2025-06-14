import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "あなたは株の専門アシスタントです。株に関する質問以外には答えないでください。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response["choices"][0]["message"]["content"]