from pydantic import BaseModel, ConfigDict, EmailStr


class TransactionSchema(BaseModel):
    title: str
    description: str
    state: str


class TransactionPublic(TransactionSchema):
    id: int


class TransactionList(BaseModel):
    transactions: list[TransactionPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    message: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserList(BaseModel):
    users: list[UserPublic]


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class FilterTransaction(FilterPage):
    title: str | None = None
    description: str | None = None
    state: str | None = None


class TransactionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: str | None = None
