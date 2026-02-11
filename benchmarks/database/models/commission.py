import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from benchmarks.database.core import Base


class RateType(enum.Enum):
    FLAT = "FLAT"
    PERCENTAGE = "PERCENTAGE"


class CommissionRate(Base):
    __tablename__ = "commission_rates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    base_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_type: Mapped[RateType] = mapped_column(Enum(RateType), nullable=False)

    user = relationship("User", back_populates="commission_rate")
    commission_result = relationship(
        "CommissionResult", back_populates="commission_rate"
    )

    @staticmethod
    async def get_by_user_id(
        user_id: int, db_session: AsyncSession
    ) -> "CommissionRate | None":
        commission_rate = await db_session.execute(
            select(CommissionRate).where(CommissionRate.user_id == user_id)
        )
        return commission_rate.scalar_one_or_none()


class CommissionResult(Base):
    __tablename__ = "commission_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    commission_rate_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("commission_rates.id"), nullable=False
    )
    total_commission: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_earnings: Mapped[int] = mapped_column(BigInteger, nullable=False)

    commission_rate = relationship("CommissionRate", back_populates="commission_result")

    @staticmethod
    async def get_by_commission_rate(
        commission_rate_id: int, db_session: AsyncSession
    ) -> "CommissionResult | None":
        commission_result = await db_session.execute(
            select(CommissionResult).where(
                CommissionResult.commission_rate_id == commission_rate_id
            )
        )
        return commission_result.scalar_one_or_none()
