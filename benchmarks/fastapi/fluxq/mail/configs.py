from .core import EmailConfig


def create_welcome_email(name: str, username: str, email: str) -> EmailConfig:
    return EmailConfig(
        header="Welcome to FluxQueue!",
        content=(
            f"Hi {name} (@{username}),"
            f"Welcome to FluxQueue! We're thrilled to have you join our community. "
            f"Your registered email is {email}. "
            "Get started by exploring your dashboard and adding your first tasks. "
            "We're here to help you stay organized and productive! "
            "Happy tasking! "
            "- The FluxQueue Team"
        ),
        middle_content=None,
        footer_top="Thanks for using FluxQueue.",
        footer_bottom="© 2026 FluxQueue. All rights reserved.",
    )
