import logging

from sqlalchemy import text

from src.db.engine import async_session
from src.services.llm_service import parse_intent
from src.services.sql_builder import build_query

logger = logging.getLogger(__name__)


async def process_query(user_text: str) -> str:
    """Process a natural language query and return a single number as string."""
    try:
        intent = await parse_intent(user_text)
        logger.info("Intent: %s", intent.model_dump_json())
    except ValueError as e:
        logger.warning("Ошибка парсинга intent: %s", e)
        return f"Не удалось распознать запрос: {e}"
    except Exception as e:
        logger.error("Ошибка LLM: %s", e)
        return "Ошибка при обращении к LLM. Попробуйте позже."

    try:
        sql, params = build_query(intent)
        logger.info("SQL: %s | Params: %s", sql, params)
    except Exception as e:
        logger.error("Ошибка построения SQL: %s", e)
        return "Ошибка при построении запроса."

    try:
        async with async_session() as session:
            result = await session.execute(text(sql), params)
            value = result.scalar()
            return str(int(value)) if value is not None else "0"
    except Exception as e:
        logger.error("Ошибка выполнения SQL: %s", e)
        return "Ошибка при выполнении запроса к базе данных."
