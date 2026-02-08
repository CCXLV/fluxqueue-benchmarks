from pydantic import BaseModel


class WelcomeEmailBody(BaseModel):
    username: str
    name: str
    email: str
