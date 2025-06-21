from pydantic import BaseModel, ConfigDict, EmailStr


class TaskSchema(BaseModel):
    title: str
    description: str
    state: str


class TaskPublic(TaskSchema):
    id: int


class TaskList(BaseModel):
    tasks: list[TaskPublic]


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


class FilterTask(FilterPage):
    title: str | None = None
    description: str | None = None
    state: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: str | None = None
