from groq import Groq
from dotenv import load_dotenv
import os
from typing import Any

load_dotenv()


class Function:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def get_answer(self, chain_messages: Any) -> str:
        completion = self.client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=chain_messages,
            temperature=0,
            max_completion_tokens=10000,
            top_p=1,
            stream=False,
            stop=None,
        )
        r = completion.choices[0].message.content
        return r or "К сожалению, я не понимаю. Пожалуйста, попробуйте еще раз."


fn = Function()
