import os
import smtplib
from contextlib import asynccontextmanager, contextmanager, suppress
from email.message import EmailMessage
from typing import TypedDict

import aiosmtplib
from fastapi.templating import Jinja2Templates

from benchmarks.config import BASE_DIR, DOCS_URL, LOGO_URL

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


@contextmanager
def get_email_client_sync():
    client = smtplib.SMTP("localhost", 2525)
    try:
        yield client
    finally:
        with suppress(Exception):
            client.quit()


@asynccontextmanager
async def get_email_client_async():
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


def send_email_sync(
    *,
    email_client: smtplib.SMTP,
    to_email: str,
    subject: str,
    config: EmailConfig,
    template: str = "emails/template.html",
):
    html_content = templates.get_template(template).render(
        docs_url=DOCS_URL,
        logo_url=LOGO_URL,
        **config,
    )

    message = EmailMessage()
    message["From"] = "fluxqueue-benchmarks@test.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(html_content, subtype="html")

    email_client.send_message(message)


async def send_email_async(
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
