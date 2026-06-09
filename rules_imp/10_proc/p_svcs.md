# Services Monitoring - Мониторинг сервисов

> Глобальное правило для ВСЕХ проектов
> Создано: 24.02.2026

---

## 🎯 Цель

Автоматический мониторинг и управление сервисами перед их использованием.

---

## 📂 Расположение .bat файлов

```
C:\RPG\project\Opal\cmd\
├── _01.GigaChat3-10B-A1.8B.bat   → LLM (порт 5001)
├── _02.Start_Embeding_model.bat  → Embeddings (порт 5002)
├── _03.Start_Reranking_model.bat → Reranker (порт 5003)
└── _04.Start_qdrant.bat          → Qdrant (порт 6333)
```

---

## 🔧 Сервисы и порты

| Сервис | Порт | .bat файл | Таймаут загрузки |
|--------|------|-----------|------------------|
| LLM | 5001 | `_01.GigaChat3-10B-A1.8B.bat` | 20-30 сек |
| Embeddings | 5002 | `_02.Start_Embeding_model.bat` | 10-15 сек |
| Reranker | 5003 | `_03.Start_Reranking_model.bat` | 10-15 сек |
| Qdrant | 6333 | `_04.Start_qdrant.bat` | 5-10 сек |

---

## 📊 3 состояния сервисов

| Состояние | Признак | Действие |
|-----------|---------|----------|
| ❌ **НЕ ЗАПУЩЕНА** | Нет ответа на `/health` | Запустить .bat, ждать 20-30 сек |
| 🔄 **ЗАГРУЖАЕТСЯ** | Сервер отвечает, но модель не готова | Ждать 10-15 сек, проверить снова |
| ✅ **РАБОТАЕТ** | Модель отвечает корректно | Использовать |

---

## 🔍 Алгоритм проверки

```python
def check_service(name, url, bat_file, timeout=30):
    """
    Проверить состояние сервиса.
    
    Returns:
        "NOT_RUNNING" - не запущена
        "LOADING" - загружается
        "READY" - работает
    """
    try:
        response = requests.get(f"{url}/health", timeout=2)
        if response.status_code == 200:
            return "READY"
        else:
            return "LOADING"
    except:
        return "NOT_RUNNING"

def ensure_service_ready(name, url, bat_file):
    """Гарантировать что сервис готов к работе."""
    state = check_service(name, url, bat_file)
    
    if state == "READY":
        print(f"  [{name}] ✅ РАБОТАЕТ")
        return True
    
    elif state == "NOT_RUNNING":
        print(f"  [{name}] ❌ НЕ ЗАПУЩЕНА → запускаю...")
        subprocess.run(bat_file, shell=True)
        time.sleep(20)  # Ждать загрузки
        return ensure_service_ready(name, url, bat_file)  # Рекурсивная проверка
    
    elif state == "LOADING":
        print(f"  [{name}] 🔄 ЗАГРУЖАЕТСЯ → жду 10-15 сек...")
        time.sleep(15)
        return ensure_service_ready(name, url, bat_file)  # Рекурсивная проверка
```

---

## ⚠️ Важно

1. **НЕ запускать сервисы если они уже работают**
2. **LLM загружается дольше всех** (20-30 сек)
3. **Перед использованием ЛЮБОГО сервиса - проверить состояние**
4. **Логировать все действия** с сервисами

---

## 📝 Чек-лист перед запуском сценария

```
[ ] Проверить LLM (5001)
[ ] Проверить Embeddings (5002)
[ ] Проверить Reranker (5003)
[ ] Проверить Qdrant (6333)
[ ] Все сервисы готовы → запускать сценарий
```

---

*Это правило действует во ВСЕХ проектах пользователя.*