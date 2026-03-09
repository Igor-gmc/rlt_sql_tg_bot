"""
Комплексный E2E-тест: вопросы → intent → SQL → PostgreSQL → число.

Кейсы определены в test_cases.py.
Запуск: pytest src/tests/test_e2e_queries.py -v
"""

from datetime import date

import pytest

from src.services.intent_schema import Filters, QueryIntent
from src.services.sql_builder import build_query
from src.tests.test_cases import E2E_CASES


# ============================================================
# Часть 1: Тест SQL Builder — проверяем генерацию SQL
# ============================================================


class TestSqlBuilderComprehensive:
    """Проверяем, что SQL Builder генерирует корректные запросы для всех типов."""

    def test_count_all_videos(self):
        intent = QueryIntent(source="videos", aggregation="count")
        sql, params = build_query(intent)
        assert sql == "SELECT COUNT(*) FROM videos"

    def test_count_by_creator(self):
        intent = QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(creator_id="abc"),
        )
        sql, _ = build_query(intent)
        assert "creator_id = :creator_id" in sql
        assert "date" not in sql.lower()

    def test_count_by_creator_and_date_range(self):
        intent = QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(
                creator_id="abc",
                date_from=date(2025, 11, 1),
                date_to=date(2025, 11, 5),
            ),
        )
        sql, params = build_query(intent)
        assert "creator_id = :creator_id" in sql
        assert "video_created_at::date BETWEEN :date_from AND :date_to" in sql

    def test_count_by_threshold_views(self):
        intent = QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="views", threshold_op=">", threshold_value=100000),
        )
        sql, _ = build_query(intent)
        assert "views_count > :threshold_value" in sql

    def test_count_by_threshold_likes(self):
        intent = QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="likes", threshold_op=">", threshold_value=50),
        )
        sql, _ = build_query(intent)
        assert "likes_count > :threshold_value" in sql

    def test_sum_views_from_videos(self):
        intent = QueryIntent(source="videos", aggregation="sum", metric="views")
        sql, _ = build_query(intent)
        assert "SUM(views_count)" in sql
        assert "delta" not in sql

    def test_sum_views_from_videos_with_dates(self):
        intent = QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 6, 1), date_to=date(2025, 6, 30)),
        )
        sql, _ = build_query(intent)
        assert "SUM(views_count)" in sql
        assert "video_created_at::date" in sql

    def test_sum_delta_views_from_snapshots(self):
        intent = QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        )
        sql, _ = build_query(intent)
        assert "SUM(delta_views_count)" in sql
        assert "AT TIME ZONE 'UTC'" in sql

    def test_count_distinct_views(self):
        intent = QueryIntent(
            source="video_snapshots", aggregation="count_distinct", metric="views",
            filters=Filters(date_from=date(2025, 11, 27), date_to=date(2025, 11, 27)),
        )
        sql, _ = build_query(intent)
        assert "COUNT(DISTINCT video_id)" in sql
        assert "delta_views_count > 0" in sql

    def test_threshold_delta(self):
        intent = QueryIntent(
            source="video_snapshots", aggregation="count",
            filters=Filters(
                threshold_field="views", threshold_op="<",
                threshold_value=0, threshold_is_delta=True,
            ),
        )
        sql, _ = build_query(intent)
        assert "delta_views_count < :threshold_value" in sql


# ============================================================
# Часть 2: E2E — intent → SQL → PostgreSQL (docker exec)
# ============================================================


def _run_sql_via_docker(sql: str, params: dict) -> int:
    """Выполняет SQL через docker exec psql и возвращает числовой результат."""
    import subprocess

    final_sql = sql
    for key, value in params.items():
        placeholder = f":{key}"
        if isinstance(value, date):
            final_sql = final_sql.replace(placeholder, f"'{value.isoformat()}'")
        elif isinstance(value, str):
            safe_val = value.replace("'", "''")
            final_sql = final_sql.replace(placeholder, f"'{safe_val}'")
        else:
            final_sql = final_sql.replace(placeholder, str(value))

    result = subprocess.run(
        [
            "docker", "exec", "rlt_sql_tg_bot-db-1",
            "psql", "-U", "postgres", "-d", "rlt_videos",
            "-t", "-A", "-c", final_sql,
        ],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql error: {result.stderr}")
    return int(result.stdout.strip())


@pytest.mark.parametrize(
    "description,intent,expected",
    E2E_CASES,
    ids=[c[0] for c in E2E_CASES],
)
def test_sql_builder_output(description: str, intent: QueryIntent, expected: int):
    """Проверяем, что SQL Builder генерирует корректный SQL без ошибок."""
    sql, params = build_query(intent)
    assert sql, f"Пустой SQL для: {description}"
    assert "SELECT" in sql


@pytest.mark.parametrize(
    "description,intent,expected",
    E2E_CASES,
    ids=[c[0] for c in E2E_CASES],
)
def test_e2e_query_result(description: str, intent: QueryIntent, expected: int):
    """E2E: intent → SQL → PostgreSQL (через docker) → сверяем с эталоном."""
    sql, params = build_query(intent)
    actual = _run_sql_via_docker(sql, params)

    assert actual == expected, (
        f"\n  Вопрос: {description}"
        f"\n  SQL: {sql}"
        f"\n  Params: {params}"
        f"\n  Ожидалось: {expected}"
        f"\n  Получено: {actual}"
    )
