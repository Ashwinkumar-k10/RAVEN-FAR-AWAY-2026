from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime, func
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./raven_incidents.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    victim_count = Column(Integer, nullable=False)
    severity_score = Column(Float, nullable=False)
    tier = Column(String, nullable=False) # Minor, Serious, Critical
    semantic_assessment = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
