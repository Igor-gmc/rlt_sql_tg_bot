import json
import logging
import re

from openai import AsyncOpenAI

from src.config import settings
from src.services.intent_schema import QueryIntent

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """Ты — аналитический ассистент. Твоя задача — преобразовать вопрос пользователя на русском языке в структурированный JSON-intent для запроса к базе данных видео-статистики.

## Схема базы данных

### Таблица `videos` — итоговая статистика по каждому видео:
- id (UUID) — идентификатор видео
- creator_id (string) — идентификатор креатора
- video_created_at (timestamp) — дата и время публикации видео
- views_count (int) — финальное количество просмотров
- likes_count (int) — финальное количество лайков
- comments_count (int) — финальное количество комментариев
- reports_count (int) — финальное количество жалоб

### Таблица `video_snapshots` — почасовые замеры статистики:
- video_id (UUID) — ссылка на видео
- delta_views_count (int) — прирост просмотров с прошлого замера
- delta_likes_count (int) — прирост лайков с прошлого замера
- delta_comments_count (int) — прирост комментариев с прошлого замера
- delta_reports_count (int) — прирост жалоб с прошлого замера
- created_at (timestamp) — время замера

## Правила выбора таблицы
- Вопросы про общее количество видео, видео креатора, видео с определённым порогом итоговой метрики → source: "videos"
- Вопросы про прирост/рост метрик за день/период → source: "video_snapshots"
- Вопросы про "сколько разных видео получали новые [метрики]" → source: "video_snapshots"
- Вопросы про замеры/снапшоты с определёнными характеристиками дельт (прирост за час, отрицательный прирост и т.д.) → source: "video_snapshots"

## Правила выбора aggregation
- "сколько видео" → "count"
- "сколько замеров/снапшотов" → "count" (source: "video_snapshots")
- "сколько разных видео" → "count_distinct"
- "на сколько выросли за день/период" → "sum" (source: "video_snapshots", суммируем delta_*)
- "суммарное/общее количество просмотров/лайков у видео" → "sum" (source: "videos", суммируем итоговые значения)

## ВАЖНО: выбор source для sum
- Если вопрос про суммарный ПРИРОСТ за конкретный день/период → source: "video_snapshots" (суммируем delta_* колонки)
- Если вопрос про суммарное ИТОГОВОЕ количество просмотров/лайков у видео (возможно с фильтром по дате публикации) → source: "videos" (суммируем итоговые views_count/likes_count и т.д.)

## Правила выбора metric
- просмотры → "views"
- лайки → "likes"
- комментарии → "comments"
- жалобы → "reports"
- если вопрос просто "сколько видео" без метрики → metric: null

## Правило threshold_is_delta
- Если вопрос про порог по ИТОГОВЫМ значениям (например, "набрало больше 100000 просмотров") → threshold_is_delta: false
- Если вопрос про порог по ПРИРОСТУ/ИЗМЕНЕНИЮ за замер (например, "прирост за час отрицательный", "число просмотров за час стало меньше", "дельта просмотров < 0") → threshold_is_delta: true
- Ключевые слова для threshold_is_delta=true: "за час", "прирост", "изменение", "дельта", "по сравнению с предыдущим замером", "стало меньше/больше по сравнению с предыдущим"

## Правило datetime_from / datetime_to
- Если в вопросе указан КОНКРЕТНЫЙ ВРЕМЕННОЙ ДИАПАЗОН с часами (например, "с 10:00 до 15:00 28 ноября 2025"), используй datetime_from и datetime_to вместо date_from и date_to
- Формат: "YYYY-MM-DDTHH:MM:SS" (ISO 8601 без таймзоны)
- datetime фильтры применяются к полю created_at в video_snapshots
- Если указан только день без часов — используй date_from/date_to
- ВАЖНО: НЕ используй date_from/date_to одновременно с datetime_from/datetime_to

## Формат ответа
Верни ТОЛЬКО валидный JSON (без markdown, без пояснений):
{
  "source": "videos" | "video_snapshots",
  "aggregation": "count" | "count_distinct" | "sum",
  "metric": "views" | "likes" | "comments" | "reports" | null,
  "filters": {
    "creator_id": "string" | null,
    "date_from": "YYYY-MM-DD" | null,
    "date_to": "YYYY-MM-DD" | null,
    "datetime_from": "YYYY-MM-DDTHH:MM:SS" | null,
    "datetime_to": "YYYY-MM-DDTHH:MM:SS" | null,
    "threshold_field": "views" | "likes" | "comments" | "reports" | null,
    "threshold_op": ">" | ">=" | "<" | "<=" | "=" | null,
    "threshold_value": число | null,
    "threshold_is_delta": true | false
  }
}

## Примеры

Вопрос: "Сколько всего видео есть в системе?"
{"source":"videos","aggregation":"count","metric":null,"filters":{}}

Вопрос: "Сколько видео у креатора с id abc123 вышло с 1 ноября 2025 по 5 ноября 2025 включительно?"
{"source":"videos","aggregation":"count","metric":null,"filters":{"creator_id":"abc123","date_from":"2025-11-01","date_to":"2025-11-05"}}

Вопрос: "Сколько видео набрало больше 100000 просмотров за всё время?"
{"source":"videos","aggregation":"count","metric":null,"filters":{"threshold_field":"views","threshold_op":">","threshold_value":100000}}

Вопрос: "Какое суммарное количество просмотров набрали все видео, опубликованные в июне 2025 года?"
{"source":"videos","aggregation":"sum","metric":"views","filters":{"date_from":"2025-06-01","date_to":"2025-06-30"}}

Вопрос: "На сколько просмотров в сумме выросли все видео 28 ноября 2025?"
{"source":"video_snapshots","aggregation":"sum","metric":"views","filters":{"date_from":"2025-11-28","date_to":"2025-11-28"}}

Вопрос: "Сколько разных видео получали новые просмотры 27 ноября 2025?"
{"source":"video_snapshots","aggregation":"count_distinct","metric":"views","filters":{"date_from":"2025-11-27","date_to":"2025-11-27"}}

Вопрос: "Сколько замеров статистики, в которых число просмотров за час оказалось отрицательным?"
{"source":"video_snapshots","aggregation":"count","metric":null,"filters":{"threshold_field":"views","threshold_op":"<","threshold_value":0,"threshold_is_delta":true}}

Вопрос: "Сколько снапшотов с приростом лайков больше 10?"
{"source":"video_snapshots","aggregation":"count","metric":null,"filters":{"threshold_field":"likes","threshold_op":">","threshold_value":10,"threshold_is_delta":true}}

Вопрос: "На сколько просмотров суммарно выросли все видео креатора с id cd87be38b50b4fdd8342bb3c383f3c7d в промежутке с 10:00 до 15:00 28 ноября 2025 года?"
{"source":"video_snapshots","aggregation":"sum","metric":"views","filters":{"creator_id":"cd87be38b50b4fdd8342bb3c383f3c7d","datetime_from":"2025-11-28T10:00:00","datetime_to":"2025-11-28T15:00:00"}}

Если вопрос не относится к статистике видео или невозможно определить intent, верни:
{"error": "unsupported"}"""


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try to find JSON in code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Try to parse the whole text as JSON
    text = text.strip()
    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])
    raise ValueError(f"Не удалось извлечь JSON из ответа LLM: {text[:200]}")


async def parse_intent(user_text: str) -> QueryIntent:
    """Parse user's natural language query into a structured QueryIntent."""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0,
        max_tokens=500,
    )

    content = response.choices[0].message.content
    logger.info("LLM response: %s", content)

    data = _extract_json(content)

    if "error" in data:
        raise ValueError(f"LLM вернула ошибку: {data['error']}")

    return QueryIntent.model_validate(data)
