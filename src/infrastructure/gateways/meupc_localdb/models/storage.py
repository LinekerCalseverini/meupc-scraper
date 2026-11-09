from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.gateways.meupc_localdb.database import Base


class StorageSqlModel(Base):
    __tablename__ = "storages"

    hash_: Mapped[str] = mapped_column("hash", String, primary_key=True)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    series: Mapped[str] = mapped_column(String, nullable=False)
    format_: Mapped[str] = mapped_column("format", String, nullable=False)
    type_: Mapped[str] = mapped_column("type", String, nullable=False)
    capacity_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    read: Mapped[int] = mapped_column(Integer, nullable=False)
    write: Mapped[int] = mapped_column(Integer, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    price_slip_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    sponsored: Mapped[bool] = mapped_column(Boolean, nullable=False)
