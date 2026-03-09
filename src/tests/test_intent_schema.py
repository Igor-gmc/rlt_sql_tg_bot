import pytest
from pydantic import ValidationError

from src.services.intent_schema import Filters, QueryIntent


class TestFilters:
    def test_empty_filters(self):
        f = Filters()
        assert f.creator_id is None
        assert f.date_from is None

    def test_threshold_all_or_none(self):
        with pytest.raises(ValidationError):
            Filters(threshold_field="views", threshold_op=">")

    def test_threshold_complete(self):
        f = Filters(threshold_field="views", threshold_op=">", threshold_value=100)
        assert f.threshold_value == 100

    def test_dates_order(self):
        with pytest.raises(ValidationError):
            Filters(date_from="2025-11-05", date_to="2025-11-01")

    def test_dates_valid(self):
        f = Filters(date_from="2025-11-01", date_to="2025-11-05")
        assert f.date_from.isoformat() == "2025-11-01"


class TestQueryIntent:
    def test_count_videos_total(self):
        intent = QueryIntent(source="videos", aggregation="count")
        assert intent.metric is None

    def test_sum_requires_metric(self):
        with pytest.raises(ValidationError):
            QueryIntent(source="video_snapshots", aggregation="sum")

    def test_count_distinct_requires_metric(self):
        with pytest.raises(ValidationError):
            QueryIntent(source="video_snapshots", aggregation="count_distinct")

    def test_count_distinct_requires_snapshots(self):
        with pytest.raises(ValidationError):
            QueryIntent(
                source="videos", aggregation="count_distinct", metric="views"
            )

    def test_sum_with_metric(self):
        intent = QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views"
        )
        assert intent.metric == "views"

    def test_invalid_source(self):
        with pytest.raises(ValidationError):
            QueryIntent(source="unknown", aggregation="count")

    def test_invalid_metric(self):
        with pytest.raises(ValidationError):
            QueryIntent(
                source="video_snapshots", aggregation="sum", metric="unknown"
            )

    def test_full_intent_with_filters(self):
        intent = QueryIntent(
            source="videos",
            aggregation="count",
            filters={
                "creator_id": "abc123",
                "date_from": "2025-11-01",
                "date_to": "2025-11-05",
            },
        )
        assert intent.filters.creator_id == "abc123"
