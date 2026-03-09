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
        delta_col = DELTA_COLUMNS[intent.metric]
        select = f"SELECT COALESCE(SUM({delta_col}), 0)"
    elif intent.aggregation == "count_distinct":
        delta_col = DELTA_COLUMNS[intent.metric]
        select = "SELECT COUNT(DISTINCT video_id)"
        conditions.append(f"{delta_col} > 0")

    # FROM clause
    from_clause = f"FROM {intent.source}"

    # WHERE conditions
    f = intent.filters

    if f.creator_id is not None:
        conditions.append("creator_id = :creator_id")
        params["creator_id"] = f.creator_id

    if f.date_from is not None or f.date_to is not None:
        if intent.source == "videos":
            date_col = "video_created_at::date"
        else:
            date_col = "(created_at AT TIME ZONE 'UTC')::date"

        if f.date_from is not None and f.date_to is not None:
            if f.date_from == f.date_to:
                conditions.append(f"{date_col} = :date_from")
                params["date_from"] = f.date_from.isoformat()
            else:
                conditions.append(f"{date_col} BETWEEN :date_from AND :date_to")
                params["date_from"] = f.date_from.isoformat()
                params["date_to"] = f.date_to.isoformat()
        elif f.date_from is not None:
            conditions.append(f"{date_col} >= :date_from")
            params["date_from"] = f.date_from.isoformat()
        else:
            conditions.append(f"{date_col} <= :date_to")
            params["date_to"] = f.date_to.isoformat()

    if f.threshold_field is not None:
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
