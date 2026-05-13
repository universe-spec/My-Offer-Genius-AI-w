# ai/llm_client.py
"""大模型调用客户端"""

import os
import requests

from dotenv import load_dotenv
load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "").strip()
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1").strip()
        self.model = os.getenv("LLM_MODEL", "deepseek-chat").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.base_url)

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
        if not self.enabled:
            return ""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        try:
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=payload, timeout=40)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print("LLM调用失败:", e)
            return ""


# 全局单例，其他模块直接 import 使用
llm = LLMClient()