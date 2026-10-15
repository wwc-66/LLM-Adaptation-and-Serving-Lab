"""
Teacher Model 调用器：调用外部 API 生成参考答案。
当前实现：仅支持 openai_compatible（DeepSeek / Ollama 等）。
"""

import time
import requests

def call_teacher(
    prompt: str,
    model: str = "qwen3.8:27b",
    provider: str = "openai_compatible",
    api_key: str = "ollama",
    base_url: str = "http://localhost:11434/v1",
    max_retries: int = 3,
    timeout: int = 180,
    backoff_base: float = 0.5,
) -> dict:
    """
    调用 Teacher Model 生成答案。
    返回：
      {
        "response": str,          # 成功时是回答；失败时是空串
        "attempts": int,          # 实际尝试次数
        "error": str | None,      # 失败时的错误信息
        "latency_ms": float,      # 总耗时
      }
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    start_time = time.perf_counter()
    attempts = 0
    last_error = None

    #重试循环+指数退避
    for attempt in range(1, max_retries+1):
        attempts = attempt
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            #空响应视为失败
            if not content or not content.strip():
                last_error = "teacher返回空响应"
                if attempt < max_retries:
                    time.sleep(backoff_base * (2 ** (attempt - 1)))
                continue

            #成功
            return {
                "response": content,
                "attempts": attempts,
                "error": None,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2)
            }

        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                time.sleep(backoff_base * (2 ** (attempt - 1)))

    #所有重试都失败
    return {
          "response": "",
          "attempts": attempts,
          "error": last_error,
          "latency_ms": round((time.perf_counter() - start_time) * 1000, 2)
    }