from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.gateways.meupc_localdb.database import Base


class PriceHistorySqlModel(Base):
    __tablename__ = "price_history"
    hash_: Mapped[str] = mapped_column("hash", String, primary_key=True)
    timestamp: Mapped[int] = mapped_column(Integer, primary_key=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
