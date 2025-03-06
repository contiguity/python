import msgspec


class Crumbs(msgspec.Struct):
    plan: str
    quota: int
    type: str
    ad: bool
