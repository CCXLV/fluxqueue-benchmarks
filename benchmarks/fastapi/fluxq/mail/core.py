import os
from contextlib import asynccontextmanager
from email.message import EmailMessage
from typing import TypedDict

import aiosmtplib
from fastapi.templating import Jinja2Templates

from benchmarks.fastapi.fluxq.config import BASE_DIR, DOCS_URL, LOGO_URL

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


class Link(TypedDict):
    href: str
    text: str


class MiddleContent(TypedDict):
    link: Link


class EmailConfig(TypedDict):
    header: str
    content: str
    middle_content: MiddleContent | None
    footer_top: str
    footer_bottom: str | None


@asynccontextmanager
async def get_email_client():
    client = aiosmtplib.SMTP(
        hostname="localhost",
        port=2525,
    )
    try:
        await client.connect()
        yield client
    finally:
        if client.is_connected:
            await client.quit()


async def send_email(
    *,
    email_client: aiosmtplib.SMTP,
    to_email: str,
    subject: str,
    config: EmailConfig,
    template: str = "emails/template.html",
):
    html_content = templates.get_template(template).render(
        docs_url=DOCS_URL, logo_url=LOGO_URL, **config
    )

    message = EmailMessage()
    message["From"] = "fluxqueue-benchmarks@test.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(html_content, subtype="html")

    await email_client.send_message(message)
