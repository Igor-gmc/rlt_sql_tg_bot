# Telegram-бот для аналитики по видео

Бот принимает вопросы на русском языке о статистике видео и возвращает одно число — результат SQL-запроса к PostgreSQL.

## Быстрый запуск (Docker)

1. Клонировать репозиторий
2. Создать файл `.env` в корне проекта:

```env
OPENAI_API_KEY=sk-proj-...
DB_NAME=rlt_videos
DB_PASSWORD=2293663
DB_USER=postgres
DB_HOST=localhost
DB_PORT=5432
BOT_TOKEN=<токен от @BotFather>
```

3. Запустить:

```bash
docker-compose up --build -d
```

При первом запуске бот автоматически создаёт таблицы и загружает данные из `data/videos.json`.

## Запуск без Docker

1. Установить PostgreSQL 15+, создать базу `rlt_videos`
2. Создать виртуальное окружение и установить зависимости:

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
source venv/Scripts/activate    # Windows (Git Bash)
pip install -r requirements.txt
```

3. Заполнить `.env` (см. выше)
4. Запустить:

```bash
python -m src.main
```

## Как задать токен Telegram-бота

1. Открыть [@BotFather](https://t.me/BotFather) в Telegram
2. Отправить `/newbot`, выбрать имя и username
3. Скопировать полученный токен в `.env`:

```env
BOT_TOKEN=8417583574:AAH...
```

## Архитектура

```
Пользователь (Telegram)
    │
    ▼
Bot Layer (aiogram) — принимает текст, отдаёт число
    │
    ▼
LLM Service (OpenAI) — NL → JSON intent
    │
    ▼
Intent Validator (Pydantic) — валидация структуры
    │
    ▼
SQL Builder — intent → SQL с bind-параметрами
    │
    ▼
DB Service (asyncpg) — выполнение SQL → одно число
```

### Принцип: LLM не пишет SQL

LLM используется **только** для semantic parsing — преобразования вопроса на русском в структурированный JSON-intent. SQL генерируется **кодом** на основе белых списков таблиц, полей, агрегаций и операторов.

Это обеспечивает:
- стабильность ответов при автопроверке
- защиту от SQL-инъекций и галлюцинаций
- прозрачную и тестируемую логику

### Пример pipeline

Вопрос: *«На сколько просмотров в сумме выросли все видео 28 ноября 2025?»*

**1. LLM возвращает JSON intent:**
```json
{
  "source": "video_snapshots",
  "aggregation": "sum",
  "metric": "views",
  "filters": {
    "date_from": "2025-11-28",
    "date_to": "2025-11-28"
  }
}
```

**2. SQL Builder генерирует запрос:**
```sql
SELECT COALESCE(SUM(delta_views_count), 0)
FROM video_snapshots
WHERE (created_at AT TIME ZONE 'UTC')::date = :date_from
```

**3. Бот отвечает:** `12345`

## Описание схемы данных для LLM

В system-промпте LLM получает:

- **Структуру таблиц** `videos` и `video_snapshots` с описанием каждого поля
- **Правила выбора таблицы**: итоговые показатели → `videos`, приросты за период → `video_snapshots`
- **Правила выбора агрегации**: «сколько видео» → `count`, «на сколько выросли» → `sum`, «сколько разных видео» → `count_distinct`
- **Маппинг метрик**: просмотры → `views`, лайки → `likes`, комментарии → `comments`, жалобы → `reports`
- **Формат ответа**: строго JSON по фиксированной схеме, без SQL, без пояснений
- **Примеры** intent для каждого типа запроса

Полный текст промпта находится в `src/services/llm_service.py` (переменная `SYSTEM_PROMPT`).

## Структура проекта

```
├── .env                              # Переменные окружения
├── .gitignore
├── docker-compose.yml                # PostgreSQL + бот
├── Dockerfile
├── requirements.txt
├── README.md
│
├── data/
│   └── videos.json                   # Исходные данные для загрузки в БД
│
├── src/
│   ├── __init__.py
│   ├── main.py                       # Точка входа: init_db, load_data, polling
│   ├── config.py                     # Настройки из .env (pydantic-settings)
│   │
│   ├── bot/
│   │   ├── __init__.py
│   │   └── handlers.py              # Telegram-хэндлеры (aiogram Router)
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py                # AsyncEngine, async_sessionmaker, init_db()
│   │   ├── loader.py                # Загрузка videos.json в БД (идемпотентно)
│   │   └── models.py                # ORM-модели: Video, VideoSnapshot
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py           # OpenAI async клиент + system prompt
│   │   ├── intent_schema.py         # Pydantic-модели: QueryIntent, Filters
│   │   ├── sql_builder.py           # Построение SQL из intent (белые списки)
│   │   └── query_service.py         # Оркестрация: NL → intent → SQL → число
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_cases.py            # 61 тестовый кейс (описание, intent, ответ)
│       ├── test_e2e_queries.py      # E2E-тесты: intent → SQL → PostgreSQL
│       ├── test_intent_schema.py    # Unit-тесты валидации Pydantic
│       └── test_sql_builder.py      # Unit-тесты генерации SQL
```

## Тестирование

```bash
# Unit-тесты SQL Builder и валидации
python -m pytest src/tests/test_sql_builder.py src/tests/test_intent_schema.py -v

# E2E-тесты (требуется запущенный PostgreSQL в Docker)
python -m pytest src/tests/test_e2e_queries.py -v
```

Тестовые кейсы определены в `src/tests/test_cases.py` — 61 сценарий, покрывающий все типы запросов: count, sum, count_distinct, фильтры по дате/datetime, threshold, creator_id, delta-метрики.

## Технологии

- **Python 3.11** — основной язык
- **aiogram 3** — асинхронный Telegram Bot API
- **SQLAlchemy 2 + asyncpg** — асинхронный ORM и драйвер PostgreSQL
- **Pydantic 2** — валидация intent-структур и настроек
- **OpenAI API (gpt-4o-mini)** — semantic parsing (NL → JSON)
- **Docker + docker-compose** — контейнеризация
- **PostgreSQL 15** — хранение данных

Весь стек асинхронный end-to-end.

## Масштабирование

### Вынос базы данных в отдельный контейнер / сервер

В текущей конфигурации PostgreSQL и бот запускаются в одном docker-compose. Для production-окружения базу данных можно вынести на отдельный сервер или в managed-сервис (AWS RDS, Yandex Managed PostgreSQL и т.д.):

1. Убрать сервис `db` из `docker-compose.yml`
2. В `.env` указать хост и порт внешней БД:
   ```env
   DB_HOST=your-db-host.example.com
   DB_PORT=5432
   ```
3. Бот подключится к внешней базе без изменения кода — все параметры берутся из переменных окружения

### Горизонтальное масштабирование бота

- Бот stateless — можно запустить несколько реплик за балансировщиком с помощью Telegram Bot API webhook-режима вместо polling
- Для переключения на webhook достаточно заменить `start_polling()` на `start_webhook()` в `src/main.py` и добавить HTTP-сервер (aiohttp/FastAPI)

### Масштабирование базы данных

- **Read replicas** — для тяжёлых аналитических запросов можно направлять SELECT-запросы на реплику
- **Индексы** — при росте данных добавить индексы на часто используемые поля (`creator_id`, `video_created_at`, `created_at`, `video_id`)
- **Партиционирование** — таблицу `video_snapshots` можно партиционировать по дате (`created_at`) для ускорения запросов по диапазонам дат
- **Пул соединений** — при большом числе запросов настроить PgBouncer перед PostgreSQL

### Кэширование

- Одинаковые вопросы часто приводят к одним и тем же SQL-запросам — можно кэшировать результаты на уровне intent (Redis / in-memory LRU)
- Кэш LLM-ответов позволит сэкономить на API-вызовах для повторяющихся формулировок
