from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, model_validator


class Filters(BaseModel):
    creator_id: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    datetime_from: datetime | None = None
    datetime_to: datetime | None = None
    threshold_field: Literal["views", "likes", "comments", "reports"] | None = None
    threshold_op: Literal[">", ">=", "<", "<=", "="] | None = None
    threshold_value: int | None = None
    threshold_is_delta: bool = False

    @model_validator(mode="after")
    def validate_threshold(self) -> "Filters":
        has_field = self.threshold_field is not None
        has_op = self.threshold_op is not None
        has_value = self.threshold_value is not None
        if has_field or has_op or has_value:
            if not (has_field and has_op and has_value):
                raise ValueError(
                    "threshold_field, threshold_op и threshold_value "
                    "должны быть заданы вместе"
                )
        return self

    @model_validator(mode="after")
    def validate_dates(self) -> "Filters":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from не может быть позже date_to")
        if self.datetime_from and self.datetime_to and self.datetime_from > self.datetime_to:
            raise ValueError("datetime_from не может быть позже datetime_to")
        return self


class QueryIntent(BaseModel):
    source: Literal["videos", "video_snapshots"]
    aggregation: Literal["count", "count_distinct", "sum"]
    metric: Literal["views", "likes", "comments", "reports"] | None = None
    distinct_field: Literal["creator_id", "video_id", "date"] | None = None
    filters: Filters = Filters()

    @model_validator(mode="after")
    def validate_intent(self) -> "QueryIntent":
        if self.aggregation == "sum" and self.metric is None:
            raise ValueError("metric обязательна для aggregation=sum")
        if self.aggregation == "count_distinct":
            if self.metric is None and self.distinct_field is None:
                raise ValueError(
                    "metric или distinct_field обязательны для aggregation=count_distinct"
                )
        return self
