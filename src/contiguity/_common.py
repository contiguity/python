from pydantic import BaseModel


class Crumbs(BaseModel):
    plan: str
    quota: int
    type: str
    ad: bool
