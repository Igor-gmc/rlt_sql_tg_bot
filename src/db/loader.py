import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from src.db.engine import async_session

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "videos.json"


async def load_data() -> None:
    async with async_session() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM videos"))
        count = result.scalar()
        if count and count > 0:
            logger.info("Данные уже загружены (%d видео), пропускаю", count)
            return

    logger.info("Загрузка данных из %s", DATA_PATH)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data["videos"]

    def parse_dt(s: str) -> datetime:
        return datetime.fromisoformat(s)

    async with async_session() as session:
        async with session.begin():
            # Insert videos
            video_rows = []
            for v in videos:
                video_rows.append({
                    "id": uuid.UUID(v["id"]),
                    "creator_id": v["creator_id"],
                    "video_created_at": parse_dt(v["video_created_at"]),
                    "views_count": v["views_count"],
                    "likes_count": v["likes_count"],
                    "comments_count": v["comments_count"],
                    "reports_count": v["reports_count"],
                    "created_at": parse_dt(v["created_at"]),
                    "updated_at": parse_dt(v["updated_at"]),
                })

            if video_rows:
                await session.execute(
                    text(
                        "INSERT INTO videos "
                        "(id, creator_id, video_created_at, views_count, "
                        "likes_count, comments_count, reports_count, "
                        "created_at, updated_at) "
                        "VALUES "
                        "(:id, :creator_id, :video_created_at, :views_count, "
                        ":likes_count, :comments_count, :reports_count, "
                        ":created_at, :updated_at)"
                    ),
                    video_rows,
                )
                logger.info("Загружено %d видео", len(video_rows))

            # Insert snapshots
            snapshot_rows = []
            for v in videos:
                for s in v.get("snapshots", []):
                    snapshot_rows.append({
                        "id": s["id"],
                        "video_id": uuid.UUID(s["video_id"]),
                        "views_count": s["views_count"],
                        "likes_count": s["likes_count"],
                        "comments_count": s["comments_count"],
                        "reports_count": s["reports_count"],
                        "delta_views_count": s["delta_views_count"],
                        "delta_likes_count": s["delta_likes_count"],
                        "delta_comments_count": s["delta_comments_count"],
                        "delta_reports_count": s["delta_reports_count"],
                        "created_at": parse_dt(s["created_at"]),
                        "updated_at": parse_dt(s["updated_at"]),
                    })

            # Batch insert snapshots in chunks of 5000
            chunk_size = 5000
            for i in range(0, len(snapshot_rows), chunk_size):
                chunk = snapshot_rows[i : i + chunk_size]
                await session.execute(
                    text(
                        "INSERT INTO video_snapshots "
                        "(id, video_id, views_count, likes_count, "
                        "comments_count, reports_count, "
                        "delta_views_count, delta_likes_count, "
                        "delta_comments_count, delta_reports_count, "
                        "created_at, updated_at) "
                        "VALUES "
                        "(:id, :video_id, :views_count, :likes_count, "
                        ":comments_count, :reports_count, "
                        ":delta_views_count, :delta_likes_count, "
                        ":delta_comments_count, :delta_reports_count, "
                        ":created_at, :updated_at)"
                    ),
                    chunk,
                )
            logger.info("Загружено %d снапшотов", len(snapshot_rows))

    logger.info("Загрузка данных завершена")
