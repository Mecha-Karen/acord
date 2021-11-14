import pydantic


class User(pydantic.BaseModel):
    verified: bool
    username: str
    mfa_enabled: bool
    id: int
    flags: int
    discriminator: int
    bot: str
    avatar: str

    email: str = None
