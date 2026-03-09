from src.services.intent_schema import QueryIntent

METRIC_COLUMNS: dict[str, str] = {
    "views": "views_count",
    "likes": "likes_count",
    "comments": "comments_count",
    "reports": "reports_count",
}

DELTA_COLUMNS: dict[str, str] = {
    "views": "delta_views_count",
    "likes": "delta_likes_count",
    "comments": "delta_comments_count",
    "reports": "delta_reports_count",
}

ALLOWED_OPS = {">", ">=", "<", "<=", "="}


def build_query(intent: QueryIntent) -> tuple[str, dict]:
    params: dict = {}
    conditions: list[str] = []

    # SELECT clause
    if intent.aggregation == "count":
        select = "SELECT COUNT(*)"
    elif intent.aggregation == "sum":
        if intent.source == "video_snapshots":
            sum_col = DELTA_COLUMNS[intent.metric]
        else:
            sum_col = METRIC_COLUMNS[intent.metric]
        select = f"SELECT COALESCE(SUM({sum_col}), 0)"
    elif intent.aggregation == "count_distinct":
        delta_col = DELTA_COLUMNS[intent.metric]
        select = "SELECT COUNT(DISTINCT video_id)"
        conditions.append(f"{delta_col} > 0")

    # FROM clause
    f = intent.filters
    need_join = (
        intent.source == "video_snapshots" and f.creator_id is not None
    )
    if need_join:
        from_clause = "FROM video_snapshots JOIN videos ON videos.id = video_snapshots.video_id"
    else:
        from_clause = f"FROM {intent.source}"

    # WHERE conditions

    if f.creator_id is not None:
        if need_join:
            conditions.append("videos.creator_id = :creator_id")
        else:
            conditions.append("creator_id = :creator_id")
        params["creator_id"] = f.creator_id

    # Table prefix for snapshot columns when JOIN is used
    snap_prefix = "video_snapshots." if need_join else ""

    if f.date_from is not None or f.date_to is not None:
        if intent.source == "videos":
            date_col = "video_created_at::date"
        else:
            date_col = f"({snap_prefix}created_at AT TIME ZONE 'UTC')::date"

        if f.date_from is not None and f.date_to is not None:
            if f.date_from == f.date_to:
                conditions.append(f"{date_col} = :date_from")
                params["date_from"] = f.date_from
            else:
                conditions.append(f"{date_col} BETWEEN :date_from AND :date_to")
                params["date_from"] = f.date_from
                params["date_to"] = f.date_to
        elif f.date_from is not None:
            conditions.append(f"{date_col} >= :date_from")
            params["date_from"] = f.date_from
        else:
            conditions.append(f"{date_col} <= :date_to")
            params["date_to"] = f.date_to

    # Datetime filters (hour-level precision for snapshots)
    if f.datetime_from is not None or f.datetime_to is not None:
        ts_col = f"{snap_prefix}created_at"
        if f.datetime_from is not None and f.datetime_to is not None:
            conditions.append(f"{ts_col} >= :datetime_from AND {ts_col} <= :datetime_to")
            params["datetime_from"] = f.datetime_from
            params["datetime_to"] = f.datetime_to
        elif f.datetime_from is not None:
            conditions.append(f"{ts_col} >= :datetime_from")
            params["datetime_from"] = f.datetime_from
        else:
            conditions.append(f"{ts_col} <= :datetime_to")
            params["datetime_to"] = f.datetime_to

    if f.threshold_field is not None:
        if f.threshold_is_delta:
            metric_col = DELTA_COLUMNS[f.threshold_field]
        else:
            metric_col = METRIC_COLUMNS[f.threshold_field]
        op = f.threshold_op
        if op not in ALLOWED_OPS:
            raise ValueError(f"Недопустимый оператор: {op}")
        conditions.append(f"{metric_col} {op} :threshold_value")
        params["threshold_value"] = f.threshold_value

    # Build final SQL
    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    sql = f"{select} {from_clause} {where}".strip()
    return sql, params
