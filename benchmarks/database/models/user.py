from sqlalchemy import BigInteger, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from benchmarks.database.core import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    earnings: Mapped[int] = mapped_column(BigInteger, nullable=False)

    commission_rate = relationship("CommissionRate", back_populates="user")

    @staticmethod
    async def get_by_email(email: str, db_session: AsyncSession) -> "User | None":
        user = await db_session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()
