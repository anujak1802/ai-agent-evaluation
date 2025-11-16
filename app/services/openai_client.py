import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_agent(model: str, prompt: str, config: dict | None = None) -> dict:
    config = config or {}
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **config
    )

    choice = completion.choices[0]
    content = choice.message.content
    usage = completion.usage

    return {
        "content": content,
        "usage": {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        }
    }
