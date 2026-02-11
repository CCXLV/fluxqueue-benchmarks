from fastapi import HTTPException

from benchmarks.database.core import session_context
from benchmarks.database.models import CommissionRate, CommissionResult, RateType, User
from benchmarks.mail.configs import create_welcome_email
from benchmarks.mail.core import (
    get_email_client,
    send_email,
)


async def send_email_task(name: str, username: str, email: str):
    email_config = create_welcome_email(name, username, email)

    async with get_email_client() as client:
        await send_email(
            email_client=client,
            to_email=email,
            subject="Welcome to FluxQueue",
            config=email_config,
        )


async def calculate_user_commission(email: str):
    async with session_context() as db_session:
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
        await db_session.commit()
