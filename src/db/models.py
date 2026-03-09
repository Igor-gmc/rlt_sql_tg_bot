import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    creator_id: Mapped[str] = mapped_column(String, nullable=False)
    video_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    views_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    snapshots: Mapped[list["VideoSnapshot"]] = relationship(
        back_populates="video"
    )


class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False
    )
    views_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delta_views_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delta_likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delta_comments_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    delta_reports_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    video: Mapped["Video"] = relationship(back_populates="snapshots")
