import re
from pathlib import Path

infra_path = Path(r"C:\Project\MIND_TEASTS\Agent_NG\core\infra.py")
content = infra_path.read_text(encoding="utf-8")

# Находим начало query_model и конец (перед read_file)
pattern = r'(def query_model\(system.*?return result\n    finally:.*?spin_thread\.join\(timeout=1\)\n)'

new_func = '''def query_model(system: str, user: str, max_tokens: int = 8192, temp: float = 0.3) -> str:
    """
    SSE streaming через legacy API — токены в реальном времени.
    Ctrl+C работает. Abort при зависании.
    """
    import json, random
    trace("query_model", {"system": system[:50], "user_len": len(user)})

    genkey = f"AGENT_{random.randint(1000, 9999)}"

    # Thinking модели — legacy API лучше работает
    payload = {
        "prompt": f"<|im_start|>system\\n{system}<|im_end|>\\n<|im_start|>user\\n{user}<|im_end|>\\n<|im_start|>assistant\\n",
        "max_context_length": 8192,
        "max_length": max_tokens,
        "temperature": temp,
        "top_p": 0.9,
        "top_k": 40,
        "rep_pen": 1.1,
        "stream": True,
        "genkey": genkey
    }

    full_text = ""
    token_count = 0
    start = time.time()
    last_token_time = time.time()
    stuck_timeout = 300  # 5 мин без токенов = зависла

    try:
        resp = requests.post(
            f"http://{HOST}:{PORT}/api/extra/generate/stream",
            json=payload,
            stream=True,
            timeout=1800
        )
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8')

            if line.startswith('data: '):
                data_str = line[6:]

                if data_str.strip() == '[DONE]':
                    break

                try:
                    data = json.loads(data_str)
                    content_token = data.get("token", "") or data.get("text", "")

                    if content_token:
                        full_text += content_token
                        token_count += 1
                        last_token_time = time.time()
                        elapsed = int(time.time() - start)
                        speed = token_count / elapsed if elapsed > 0 else 0
                        print(f"\\r[GEN] {elapsed}с | {token_count} ток | {speed:.1f} t/s | {len(full_text)} симв.", end="", flush=True)

                except json.JSONDecodeError:
                    pass

            if time.time() - last_token_time > stuck_timeout:
                print(f"\\n[WARN] Модель зависла ({stuck_timeout}с без токенов). Abort genkey={genkey}...")
                try:
                    requests.post(f"http://{HOST}:{PORT}/api/extra/abort",
                                json={"genkey": genkey}, timeout=3)
                except:
                    pass
                break

    except KeyboardInterrupt:
        print(f"\\n\\n[CTRL+C] Прервано пользователем!")
        try:
            requests.post(f"http://{HOST}:{PORT}/api/extra/abort", json={"genkey": genkey}, timeout=3)
            print("[OK] Abort отправлен")
        except:
            pass
        if not full_text.strip():
            raise SystemExit(0)
    except Exception as e:
        print(f"\\n[ERROR] {e}")

    elapsed = int(time.time() - start)
    print(f"\\n[OK] Ответ получен: {elapsed}с | {token_count} ток | {len(full_text)} симв.")

    if not full_text.strip():
        raise RuntimeError("Пустой ответ модели")

    return full_text
'''

content_new = re.sub(pattern, new_func, content, flags=re.DOTALL)

if content_new != content:
    infra_path.write_text(content_new, encoding="utf-8")
    print("OK — заменено")
else:
    print("WARNING — ничего не заменено!")
