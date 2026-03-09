from src.services.intent_schema import QueryIntent
from src.services.sql_builder import build_query


class TestSqlBuilder:
    def test_count_all_videos(self):
        intent = QueryIntent(source="videos", aggregation="count")
        sql, params = build_query(intent)
        assert sql == "SELECT COUNT(*) FROM videos"
        assert params == {}

    def test_count_videos_by_creator_and_period(self):
        intent = QueryIntent(
            source="videos",
            aggregation="count",
            filters={
                "creator_id": "abc123",
                "date_from": "2025-11-01",
                "date_to": "2025-11-05",
            },
        )
        sql, params = build_query(intent)
        assert "creator_id = :creator_id" in sql
        assert "video_created_at::date BETWEEN :date_from AND :date_to" in sql
        assert params["creator_id"] == "abc123"
        assert params["date_from"] == "2025-11-01"
        assert params["date_to"] == "2025-11-05"

    def test_count_videos_by_threshold(self):
        intent = QueryIntent(
            source="videos",
            aggregation="count",
            filters={
                "threshold_field": "views",
                "threshold_op": ">",
                "threshold_value": 100000,
            },
        )
        sql, params = build_query(intent)
        assert "views_count > :threshold_value" in sql
        assert params["threshold_value"] == 100000

    def test_sum_metric_growth(self):
        intent = QueryIntent(
            source="video_snapshots",
            aggregation="sum",
            metric="views",
            filters={"date_from": "2025-11-28", "date_to": "2025-11-28"},
        )
        sql, params = build_query(intent)
        assert "COALESCE(SUM(delta_views_count), 0)" in sql
        assert "(created_at AT TIME ZONE 'UTC')::date" in sql

    def test_count_distinct_videos(self):
        intent = QueryIntent(
            source="video_snapshots",
            aggregation="count_distinct",
            metric="views",
            filters={"date_from": "2025-11-27", "date_to": "2025-11-27"},
        )
        sql, params = build_query(intent)
        assert "COUNT(DISTINCT video_id)" in sql
        assert "delta_views_count > 0" in sql

    def test_likes_metric(self):
        intent = QueryIntent(
            source="video_snapshots",
            aggregation="sum",
            metric="likes",
            filters={"date_from": "2025-11-28", "date_to": "2025-11-28"},
        )
        sql, params = build_query(intent)
        assert "delta_likes_count" in sql

    def test_threshold_with_likes(self):
        intent = QueryIntent(
            source="videos",
            aggregation="count",
            filters={
                "threshold_field": "likes",
                "threshold_op": ">=",
                "threshold_value": 50,
            },
        )
        sql, params = build_query(intent)
        assert "likes_count >= :threshold_value" in sql

    def test_no_dates(self):
        intent = QueryIntent(
            source="videos",
            aggregation="count",
            filters={"creator_id": "abc"},
        )
        sql, params = build_query(intent)
        assert "date" not in sql.lower()
        assert "creator_id = :creator_id" in sql

    def test_single_date(self):
        intent = QueryIntent(
            source="videos",
            aggregation="count",
            filters={"date_from": "2025-11-01"},
        )
        sql, params = build_query(intent)
        assert "video_created_at::date >= :date_from" in sql

    def test_same_date_uses_equals(self):
        intent = QueryIntent(
            source="video_snapshots",
            aggregation="sum",
            metric="views",
            filters={"date_from": "2025-11-28", "date_to": "2025-11-28"},
        )
        sql, params = build_query(intent)
        assert "= :date_from" in sql
        assert "BETWEEN" not in sql
