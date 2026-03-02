from contextlib import asynccontextmanager

from fastapi import HTTPException
from fluxqueue import Context
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from benchmarks.config import SQLALCHEMY_DATABASE_URL
from benchmarks.database.core import MAX_OVERFLOW, MAX_POOL_SIZE
from benchmarks.database.models import CommissionRate, CommissionResult, RateType, User
from benchmarks.tasks import send_email_task

from .core import fluxqueue


@fluxqueue.task(name="send-email")
async def fq_send_email_task(name: str, username: str, email: str):
    await send_email_task(name, username, email)


class DbContext(Context):
    def __init__(self) -> None:
        super().__init__()

    def _get_local_session(self) -> async_sessionmaker[AsyncSession]:
        if not self.thread_storage.get("session"):
            engine = create_async_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_size=MAX_POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_timeout=30,
                pool_pre_ping=True,
                pool_recycle=3600,
            )

            self.thread_storage["session"] = async_sessionmaker(
                bind=engine, expire_on_commit=False
            )

        return self.thread_storage["session"]

    @asynccontextmanager
    async def session_context(self):
        local_session = self._get_local_session()
        async with local_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


@fluxqueue.task_with_context(name="calculate-commission")
async def fq_calculate_commission_task(ctx: DbContext, email: str):
    async with ctx.session_context() as db_session:
        user = await User.get_by_email(email, db_session)

        if not user:
            raise HTTPException(404, "User not found")

        user_commission_rate = await CommissionRate.get_by_user_id(user.id, db_session)

        if not user_commission_rate:
            raise HTTPException(404, "Commission rates not found")

        results_already_exists = await CommissionResult.get_by_commission_rate(
            user_commission_rate.id, db_session
        )

        if results_already_exists:
            raise HTTPException(400, "Commission rates are already calculated")

        total_commission = user_commission_rate.base_rate
        if user_commission_rate.rate_type == RateType.PERCENTAGE:
            total_commission = user.earnings * (user_commission_rate.base_rate / 100)

        commission_result = CommissionResult(
            commission_rate_id=user_commission_rate.id,
            total_commission=total_commission,
            total_earnings=user.earnings - total_commission,
        )
        db_session.add(commission_result)
