"""
Эталонные тест-кейсы: вопрос → intent → ожидаемый ответ.

Каждый кейс — кортеж (описание, QueryIntent, ожидаемое_число).
Используется в test_e2e_queries.py для проверки SQL Builder и E2E.
"""

from datetime import date

from src.services.intent_schema import Filters, QueryIntent

E2E_CASES: list[tuple[str, QueryIntent, int]] = [
    # ================================================================
    # COUNT ALL VIDEOS
    # ================================================================
    (
        "Сколько всего видео есть в системе?",
        QueryIntent(source="videos", aggregation="count"),
        358,
    ),
    # ================================================================
    # COUNT BY CREATOR (без дат)
    # ================================================================
    (
        "Сколько видео у креатора aca1061a?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(creator_id="aca1061a9d324ecf8c3fa2bb32d7be63"),
        ),
        47,
    ),
    (
        "Сколько видео у креатора 2dade264?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(creator_id="2dade264da8a4bf4bd9cf3bd025678e7"),
        ),
        6,
    ),
    (
        "Сколько видео у креатора 706646b9?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(creator_id="706646b9c6294a52bd741ba114d6e619"),
        ),
        4,
    ),
    (
        "Сколько видео у креатора 0d775b4e?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(creator_id="0d775b4e3388419c8f60f46a37858312"),
        ),
        24,
    ),
    (
        "Сколько видео у креатора df5973c0?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(creator_id="df5973c05d90471ca1a7511e2560cfbf"),
        ),
        41,
    ),
    # ================================================================
    # COUNT BY CREATOR + DATE RANGE
    # ================================================================
    (
        "Сколько видео у креатора 8b76e572 с 1 по 5 ноября 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(
                creator_id="8b76e572635b400c9052286a56176e03",
                date_from=date(2025, 11, 1), date_to=date(2025, 11, 5),
            ),
        ),
        3,
    ),
    (
        "Сколько видео у креатора aca1061a в ноябре 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(
                creator_id="aca1061a9d324ecf8c3fa2bb32d7be63",
                date_from=date(2025, 11, 1), date_to=date(2025, 11, 30),
            ),
        ),
        10,
    ),
    # ================================================================
    # COUNT BY DATE RANGE (без креатора)
    # ================================================================
    (
        "Сколько видео опубликовано в ноябре 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(date_from=date(2025, 11, 1), date_to=date(2025, 11, 30)),
        ),
        126,
    ),
    (
        "Сколько видео вышло 1 ноября 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(date_from=date(2025, 11, 1), date_to=date(2025, 11, 1)),
        ),
        1,
    ),
    (
        "Сколько видео опубликовано в октябре 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(date_from=date(2025, 10, 1), date_to=date(2025, 10, 31)),
        ),
        103,
    ),
    (
        "Сколько видео опубликовано в сентябре 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(date_from=date(2025, 9, 1), date_to=date(2025, 9, 30)),
        ),
        55,
    ),
    (
        "Сколько видео опубликовано в августе 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(date_from=date(2025, 8, 1), date_to=date(2025, 8, 31)),
        ),
        45,
    ),
    (
        "Сколько видео опубликовано в июне 2025?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(date_from=date(2025, 6, 1), date_to=date(2025, 6, 30)),
        ),
        14,
    ),
    # ================================================================
    # COUNT BY THRESHOLD — views
    # ================================================================
    (
        "Сколько видео набрало больше 100000 просмотров?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="views", threshold_op=">", threshold_value=100000),
        ),
        5,
    ),
    (
        "Сколько видео набрало больше 50000 просмотров?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="views", threshold_op=">", threshold_value=50000),
        ),
        7,
    ),
    (
        "Сколько видео набрало больше 10000 просмотров?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="views", threshold_op=">", threshold_value=10000),
        ),
        37,
    ),
    (
        "Сколько видео набрало больше 5000 просмотров?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="views", threshold_op=">", threshold_value=5000),
        ),
        70,
    ),
    (
        "Сколько видео набрало больше 1000 просмотров?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="views", threshold_op=">", threshold_value=1000),
        ),
        256,
    ),
    # ================================================================
    # COUNT BY THRESHOLD — likes
    # ================================================================
    (
        "Сколько видео набрало больше 100 лайков?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="likes", threshold_op=">", threshold_value=100),
        ),
        48,
    ),
    (
        "Сколько видео набрало больше 50 лайков?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="likes", threshold_op=">", threshold_value=50),
        ),
        91,
    ),
    (
        "Сколько видео набрало больше 10 лайков?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="likes", threshold_op=">", threshold_value=10),
        ),
        267,
    ),
    (
        "Сколько видео набрало больше 0 лайков?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="likes", threshold_op=">", threshold_value=0),
        ),
        349,
    ),
    # ================================================================
    # COUNT BY THRESHOLD — comments, reports
    # ================================================================
    (
        "Сколько видео имеет хотя бы 1 комментарий?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="comments", threshold_op=">", threshold_value=0),
        ),
        139,
    ),
    (
        "Сколько видео имеет хотя бы 1 жалобу?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(threshold_field="reports", threshold_op=">", threshold_value=0),
        ),
        195,
    ),
    # ================================================================
    # COUNT BY CREATOR + THRESHOLD
    # ================================================================
    (
        "Сколько видео у креатора 8b76e572 набрало больше 10000 просмотров?",
        QueryIntent(
            source="videos", aggregation="count",
            filters=Filters(
                creator_id="8b76e572635b400c9052286a56176e03",
                threshold_field="views", threshold_op=">", threshold_value=10000,
            ),
        ),
        0,
    ),
    # ================================================================
    # SUM итоговых метрик FROM videos (все видео)
    # ================================================================
    (
        "Суммарное количество просмотров всех видео?",
        QueryIntent(source="videos", aggregation="sum", metric="views"),
        3326609,
    ),
    (
        "Суммарное количество лайков всех видео?",
        QueryIntent(source="videos", aggregation="sum", metric="likes"),
        99025,
    ),
    (
        "Суммарное количество комментариев всех видео?",
        QueryIntent(source="videos", aggregation="sum", metric="comments"),
        494,
    ),
    (
        "Суммарное количество жалоб всех видео?",
        QueryIntent(source="videos", aggregation="sum", metric="reports"),
        8022,
    ),
    # ================================================================
    # SUM итоговых views FROM videos BY DATE (по месяцам)
    # ================================================================
    (
        "Суммарные просмотры видео, опубликованных в июне 2025?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 6, 1), date_to=date(2025, 6, 30)),
        ),
        17668,
    ),
    (
        "Суммарные просмотры видео, опубликованных в июле 2025?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 7, 1), date_to=date(2025, 7, 31)),
        ),
        50522,
    ),
    (
        "Суммарные просмотры видео, опубликованных в августе 2025?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 8, 1), date_to=date(2025, 8, 31)),
        ),
        1537295,
    ),
    (
        "Суммарные просмотры видео, опубликованных в сентябре 2025?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 9, 1), date_to=date(2025, 9, 30)),
        ),
        1001264,
    ),
    (
        "Суммарные просмотры видео, опубликованных в октябре 2025?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 10, 1), date_to=date(2025, 10, 31)),
        ),
        433216,
    ),
    (
        "Суммарные просмотры видео, опубликованных в ноябре 2025?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 1), date_to=date(2025, 11, 30)),
        ),
        285562,
    ),
    # ================================================================
    # SUM итоговых views BY CREATOR
    # ================================================================
    (
        "Суммарные просмотры видео креатора aca1061a?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(creator_id="aca1061a9d324ecf8c3fa2bb32d7be63"),
        ),
        188294,
    ),
    (
        "Суммарные просмотры видео креатора 2dade264?",
        QueryIntent(
            source="videos", aggregation="sum", metric="views",
            filters=Filters(creator_id="2dade264da8a4bf4bd9cf3bd025678e7"),
        ),
        5275,
    ),
    # ================================================================
    # SUM delta_views FROM snapshots BY DAY
    # ================================================================
    (
        "На сколько просмотров выросли все видео 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        ),
        14639,
    ),
    (
        "На сколько просмотров выросли все видео 27 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 27), date_to=date(2025, 11, 27)),
        ),
        1411965,
    ),
    (
        "На сколько просмотров выросли все видео 29 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 29), date_to=date(2025, 11, 29)),
        ),
        13385,
    ),
    (
        "На сколько просмотров выросли все видео 30 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 30), date_to=date(2025, 11, 30)),
        ),
        30105,
    ),
    (
        "На сколько просмотров выросли все видео 26 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 26), date_to=date(2025, 11, 26)),
        ),
        1686037,
    ),
    (
        "На сколько просмотров выросли все видео 1 декабря 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 12, 1), date_to=date(2025, 12, 1)),
        ),
        3045,
    ),
    # ================================================================
    # SUM delta_views FROM snapshots BY DATE RANGE
    # ================================================================
    (
        "На сколько просмотров выросли все видео с 26 по 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 26), date_to=date(2025, 11, 28)),
        ),
        3112641,
    ),
    (
        "На сколько просмотров выросли все видео с 25 ноября по 1 декабря 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="views",
            filters=Filters(date_from=date(2025, 11, 25), date_to=date(2025, 12, 1)),
        ),
        3326609,
    ),
    # ================================================================
    # SUM delta likes/comments/reports FROM snapshots
    # ================================================================
    (
        "На сколько лайков выросли все видео 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="likes",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        ),
        255,
    ),
    (
        "На сколько лайков выросли все видео 27 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="likes",
            filters=Filters(date_from=date(2025, 11, 27), date_to=date(2025, 11, 27)),
        ),
        28249,
    ),
    (
        "На сколько комментариев выросли все видео 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="comments",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        ),
        1,
    ),
    (
        "На сколько жалоб выросли все видео 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="sum", metric="reports",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        ),
        46,
    ),
    # ================================================================
    # COUNT DISTINCT video_id — views
    # ================================================================
    (
        "Сколько разных видео получали новые просмотры 27 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="count_distinct", metric="views",
            filters=Filters(date_from=date(2025, 11, 27), date_to=date(2025, 11, 27)),
        ),
        226,
    ),
    (
        "Сколько разных видео получали новые просмотры 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="count_distinct", metric="views",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        ),
        105,
    ),
    (
        "Сколько разных видео получали новые просмотры 29 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="count_distinct", metric="views",
            filters=Filters(date_from=date(2025, 11, 29), date_to=date(2025, 11, 29)),
        ),
        107,
    ),
    # ================================================================
    # COUNT DISTINCT video_id — likes
    # ================================================================
    (
        "Сколько разных видео получали новые лайки 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="count_distinct", metric="likes",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        ),
        25,
    ),
    (
        "Сколько разных видео получали новые лайки 27 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="count_distinct", metric="likes",
            filters=Filters(date_from=date(2025, 11, 27), date_to=date(2025, 11, 27)),
        ),
        194,
    ),
    # ================================================================
    # COUNT DISTINCT video_id — comments
    # ================================================================
    (
        "Сколько разных видео получали новые комментарии 28 ноября 2025?",
        QueryIntent(
            source="video_snapshots", aggregation="count_distinct", metric="comments",
            filters=Filters(date_from=date(2025, 11, 28), date_to=date(2025, 11, 28)),
        ),
        1,
    ),
    # ================================================================
    # NEGATIVE DELTAS (threshold_is_delta=True)
    # ================================================================
    (
        "Сколько замеров с отрицательным приростом просмотров?",
        QueryIntent(
            source="video_snapshots", aggregation="count",
            filters=Filters(
                threshold_field="views", threshold_op="<",
                threshold_value=0, threshold_is_delta=True,
            ),
        ),
        24,
    ),
    (
        "Сколько замеров с отрицательным приростом лайков?",
        QueryIntent(
            source="video_snapshots", aggregation="count",
            filters=Filters(
                threshold_field="likes", threshold_op="<",
                threshold_value=0, threshold_is_delta=True,
            ),
        ),
        46,
    ),
    (
        "Сколько замеров с отрицательным приростом комментариев?",
        QueryIntent(
            source="video_snapshots", aggregation="count",
            filters=Filters(
                threshold_field="comments", threshold_op="<",
                threshold_value=0, threshold_is_delta=True,
            ),
        ),
        0,
    ),
    (
        "Сколько замеров с отрицательным приростом жалоб?",
        QueryIntent(
            source="video_snapshots", aggregation="count",
            filters=Filters(
                threshold_field="reports", threshold_op="<",
                threshold_value=0, threshold_is_delta=True,
            ),
        ),
        1,
    ),
    # ================================================================
    # COUNT ALL SNAPSHOTS
    # ================================================================
    (
        "Сколько всего замеров статистики в системе?",
        QueryIntent(source="video_snapshots", aggregation="count"),
        35946,
    ),
]
