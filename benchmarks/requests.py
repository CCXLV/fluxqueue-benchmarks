from pydantic import BaseModel


class BasicDataRequest(BaseModel):
    username: str
    name: str
    email: str
